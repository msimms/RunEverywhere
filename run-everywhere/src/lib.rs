// Copyright (c) 2021 Michael J. Simms. All rights reserved.

extern crate gpx;

mod utils;
mod location_analyzer;

use wasm_bindgen::prelude::*;
use std::io::BufReader;

// When the `wee_alloc` feature is enabled, use `wee_alloc` as the global allocator.
#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

#[wasm_bindgen]
extern {
    fn alert(s: &str);
}

#[wasm_bindgen]
pub fn greet() {
    alert("Copyright (c) 2021 Michael J. Simms. All rights reserved.");
}

#[wasm_bindgen]
pub fn analyze_gpx(s: &str) -> String {
    utils::set_panic_hook();

    let mut analysis_report_str = String::new();

    let data = BufReader::new(s.as_bytes());
    let res = gpx::read(data);

    match res {
        Ok(gpx) => {
            let mut analyzer = location_analyzer::LocationAnalyzer::new();

            // Iterate through the tracks.
            for track in gpx.tracks {

                // Get the track name.
                match &track._type {
                    Some(activity_type) => analyzer.set_activity_type(activity_type.to_string()),
                    _ => {},
                }

                // Iterate through the track segments.
                for trackseg in track.segments {

                    // Check the first point.
                    for point in trackseg.points {
                        let time = point.time.unwrap().timestamp();
                        let lat = point.point().y();
                        let lon = point.point().x();
                        let alt = point.elevation.unwrap();

                        analyzer.check_location((time * 1000) as u64, lat, lon, alt);
                    }
                }
            }

            // Copy items to the final report.
            analysis_report_str = serde_json::json!({
                "Location": analyzer.location
            }).to_string();
        }
        Err(_e) => {
            alert("Error parsing GPX file.");
        }
    }

    analysis_report_str
}


#[wasm_bindgen]
pub fn analyze_tcx(s: &str) -> String {
    utils::set_panic_hook();

    let mut data = BufReader::new(s.as_bytes());
    let res = tcx::read(&mut data);
    let mut analyzer = location_analyzer::LocationAnalyzer::new();
    let activities = res.activities.unwrap();

    // A file can contain multiple activities.
    for activity in activities.activities {

        // Iterate through the laps.
        for lap in activity.laps {

            // Iterate through the tracks.
            for track in lap.tracks {

                // Iterate through each point.
                for trackpoint in track.trackpoints {
                    let time = trackpoint.time.timestamp() * 1000 + trackpoint.time.timestamp_subsec_millis() as i64;
                    let position = trackpoint.position.unwrap();
                    let altitude = trackpoint.altitude_meters.unwrap();

                    analyzer.check_location(time as u64, position.latitude, position.longitude, altitude);
                }
            }
        }
    }

    // Copy items to the final report.
    let analysis_report_str = serde_json::json!({
        "Location": analyzer.location
    }).to_string();

    analysis_report_str
}
