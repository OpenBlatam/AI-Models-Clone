//! Data Processing Module
//!
//! High-performance data processing with validation, templating, and batching.

pub mod config;
pub mod validators;
pub mod template;
pub mod processor;

// Re-exports
pub use config::DataProcessorConfig;
pub use validators::{
    validate_non_empty,
    validate_length,
    validate_batch_size,
    validate_batch_not_empty,
    validate_template,
};
pub use template::TemplateEngine;
pub use processor::DataProcessor;




