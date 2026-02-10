//! Data Processor Configuration
//!
//! Configuration structures for data processing operations.

use serde::{Serialize, Deserialize};
use crate::error::{Result, BenchmarkError};

/// Data processor configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataProcessorConfig {
    pub batch_size: usize,
    pub max_length: Option<usize>,
    pub padding: bool,
    pub truncation: bool,
    pub pad_token_id: u32,
    pub skip_empty: bool,
}

impl Default for DataProcessorConfig {
    fn default() -> Self {
        Self {
            batch_size: 32,
            max_length: Some(512),
            padding: true,
            truncation: true,
            pad_token_id: 0,
            skip_empty: false,
        }
    }
}

impl DataProcessorConfig {
    /// Validate configuration.
    pub fn validate(&self) -> Result<()> {
        if self.batch_size == 0 {
            return Err(BenchmarkError::invalid_input(
                "batch_size must be greater than 0"
            ));
        }
        
        if self.batch_size > 1024 {
            return Err(BenchmarkError::invalid_input(
                "batch_size exceeds maximum of 1024"
            ));
        }
        
        if let Some(max_len) = self.max_length {
            if max_len == 0 {
                return Err(BenchmarkError::invalid_input(
                    "max_length must be greater than 0 if provided"
                ));
            }
            
            if max_len > 32768 {
                return Err(BenchmarkError::invalid_input(
                    "max_length exceeds maximum of 32768"
                ));
            }
        }
        
        Ok(())
    }
    
    /// Create configuration with validation.
    pub fn new(
        batch_size: usize,
        max_length: Option<usize>,
        padding: bool,
        truncation: bool,
    ) -> Result<Self> {
        let config = Self {
            batch_size,
            max_length,
            padding,
            truncation,
            pad_token_id: 0,
            skip_empty: false,
        };
        
        config.validate()?;
        Ok(config)
    }
}




