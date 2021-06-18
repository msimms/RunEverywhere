// Copyright (c) 2021 Michael J. Simms. All rights reserved.

use lib_math::{graphics};

const TYPE_UNSPECIFIED_ACTIVITY_KEY: &str = "Unknown";
const TYPE_RUNNING_KEY: &str = "Running";
const TYPE_CYCLING_KEY: &str = "Cycling";

pub struct LocationAnalyzer {
    pub activity_type: String,
    pub location: String
}

impl LocationAnalyzer {
    pub fn new() -> Self {
        let analyzer = LocationAnalyzer{activity_type: TYPE_UNSPECIFIED_ACTIVITY_KEY.to_string(), location: "".to_string()};
        analyzer
    }

    /// Accessor for setting the activity type.
    pub fn set_activity_type(&mut self, activity_type: String) {
        self.activity_type = activity_type;
    }

    pub fn check_location(&mut self, date_time_ms: u64, latitude: f64, longitude: f64) {
    	let mut pt = graphics::Point::new();
        pt.x = longitude;
        pt.y = latitude;
    }
}
