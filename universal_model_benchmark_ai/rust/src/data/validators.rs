//! Data Validation
//!
//! Validation functions for data processing.

use crate::error::{Result, BenchmarkError};

/// Validate that text is not empty.
pub fn validate_non_empty(text: &str, field_name: &str) -> Result<()> {
    if text.is_empty() {
        Err(BenchmarkError::invalid_input(
            format!("{} cannot be empty", field_name)
        ))
    } else {
        Ok(())
    }
}

/// Validate text length.
pub fn validate_length(
    text: &str,
    min: usize,
    max: Option<usize>,
    field_name: &str,
) -> Result<()> {
    let len = text.len();
    
    if len < min {
        return Err(BenchmarkError::invalid_input(
            format!("{} length {} is less than minimum {}", field_name, len, min)
        ));
    }
    
    if let Some(max_len) = max {
        if len > max_len {
            return Err(BenchmarkError::invalid_input(
                format!("{} length {} exceeds maximum {}", field_name, len, max_len)
            ));
        }
    }
    
    Ok(())
}

/// Validate batch size.
pub fn validate_batch_size(batch_size: usize) -> Result<()> {
    if batch_size == 0 {
        Err(BenchmarkError::invalid_input("batch_size must be greater than 0"))
    } else if batch_size > 1024 {
        Err(BenchmarkError::invalid_input("batch_size exceeds maximum of 1024"))
    } else {
        Ok(())
    }
}

/// Validate that batch is not empty.
pub fn validate_batch_not_empty<T>(batch: &[T], batch_name: &str) -> Result<()> {
    if batch.is_empty() {
        Err(BenchmarkError::invalid_input(
            format!("{} cannot be empty", batch_name)
        ))
    } else {
        Ok(())
    }
}

/// Validate template string.
pub fn validate_template(template: &str) -> Result<()> {
    if template.is_empty() {
        return Err(BenchmarkError::invalid_input("Template cannot be empty"));
    }
    
    // Check for balanced braces
    let mut open_count = 0;
    for ch in template.chars() {
        match ch {
            '{' => open_count += 1,
            '}' => {
                if open_count == 0 {
                    return Err(BenchmarkError::invalid_input(
                        "Unmatched closing brace in template"
                    ));
                }
                open_count -= 1;
            }
            _ => {}
        }
    }
    
    if open_count > 0 {
        return Err(BenchmarkError::invalid_input(
            "Unmatched opening braces in template"
        ));
    }
    
    Ok(())
}




