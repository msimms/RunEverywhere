// Copyright (c) 2021 Michael J. Simms. All rights reserved.

extern crate gpx;

mod geojson;
mod location_analyzer;
mod utils;

use wasm_bindgen::prelude::*;
use std::io::BufReader;
use std::ffi::c_void;

// When the `wee_alloc` feature is enabled, use `wee_alloc` as the global allocator.
#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

static GEO: geojson::GeoJson = geojson::GeoJson{ features: None };

#[wasm_bindgen]
extern {
    fn alert(s: &str);
}

#[wasm_bindgen]
pub fn greet() {
    alert("Copyright (c) 2021 Michael J. Simms. All rights reserved.");
}

#[wasm_bindgen]
pub fn set_world_data(s: &str) {
    utils::set_panic_hook();

    unsafe {
        //GEO.features
    }
}

#[wasm_bindgen]
pub fn analyze_gpx(s: &str) -> String {
    utils::set_panic_hook();

    let mut analyzer = location_analyzer::LocationAnalyzer::new();
    let data = BufReader::new(s.as_bytes());
    let mut error = false;
    let res = gpx::read(data);

    match res {
        Err(_e) => {
            alert("Error parsing GPX file.");
            error = true;
        }
        Ok(gpx) => {
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
                        let lat = point.point().y();
                        let lon = point.point().x();

                        analyzer.check_location(lat, lon);
                    }
                }
            }
        }
    }

    let mut analysis_report_str = "".to_string();

    if !error
    {
        // Copy items to the final report.
        analysis_report_str = serde_json::json!({
            "Location": analyzer.location
        }).to_string();
    }

    analysis_report_str
}

#[wasm_bindgen]
pub fn analyze_tcx(s: &str) -> String {
    utils::set_panic_hook();

    let mut analyzer = location_analyzer::LocationAnalyzer::new();
    let mut data = BufReader::new(s.as_bytes());
    let mut error = false;
    let res = tcx::read(&mut data);

    match res {
        Err(_e) => {
            alert("Error parsing the TCX file.");
            error = true;
        }
        Ok(res) => {
            let activities = res.activities;
            match activities {
                None => {
                }
                Some(activities) => {
                    // A file can contain multiple activities.
                    for activity in activities.activities {
                        analyzer.set_activity_type(activity.sport);

                        // Iterate through the laps.
                        for lap in activity.laps {

                            // Iterate through the tracks.
                            for track in lap.tracks {

                                // Iterate through each point.
                                for trackpoint in track.trackpoints {

                                    // Get the position, including altitude.
                                    let position = trackpoint.position;
                                    match position {
                                        None => {
                                        }
                                        Some(position) => {
                                            analyzer.check_location(position.latitude, position.longitude);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    let mut analysis_report_str = "".to_string();

    if !error
    {
        // Copy items to the final report.
        analysis_report_str = serde_json::json!({
            "Location": analyzer.location
        }).to_string();
    }

    analysis_report_str
}

/// Called for each FIT record message as it is processed.
fn callback(_timestamp: u32, _global_message_num: u16, _local_msg_type: u8, _message_index: u16, fields: Vec<fit_file::fit_file::FitFieldValue>, context: *mut c_void) {
    let callback_context: &mut location_analyzer::LocationAnalyzer = unsafe { &mut *(context as *mut location_analyzer::LocationAnalyzer) };
}

#[wasm_bindgen]
pub fn analyze_fit(s: &[u8]) -> String {
    utils::set_panic_hook();

    let mut analyzer = location_analyzer::LocationAnalyzer::new();
    let context_ptr: *mut c_void = &mut analyzer as *mut _ as *mut c_void;

    let mut data = BufReader::new(s);
    let res = fit_file::fit_file::read(&mut data, callback, context_ptr);

    let mut error = false;

    match res {
        Err(_e) => {
            alert("Error parsing the FIT file.");
            error = true;
        }
        Ok(_res) => {
        }
    }

    // Copy items to the final report.
    let mut analysis_report_str = "".to_string();

    if !error
    {
        analysis_report_str = serde_json::json!({
            "Location": analyzer.location
        }).to_string();
    }

    analysis_report_str
}
