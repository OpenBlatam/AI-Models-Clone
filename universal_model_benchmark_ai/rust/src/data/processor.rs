//! Data Processor
//!
//! Main data processing implementation with validation and templating.
//!
//! This module provides the `DataProcessor` which handles text preprocessing,
//! batch processing, padding, truncation, and template-based prompt formatting.
//! It ensures data quality through comprehensive validation and supports
//! efficient batch operations.

use std::collections::HashMap;
use crate::error::{Result, BenchmarkError};
use super::config::DataProcessorConfig;
use super::validators::*;
use super::template::TemplateEngine;

/// High-performance data processor for text preprocessing and batch operations.
///
/// Handles validation, truncation, padding, and template-based formatting
/// for both single items and batches. Optimized for efficient batch processing.
pub struct DataProcessor {
    /// Configuration controlling processing behavior
    config: DataProcessorConfig,
    /// Template engine for variable substitution in prompts
    template_engine: TemplateEngine,
}

impl DataProcessor {
    /// Create a new data processor with optional configuration.
    ///
    /// # Arguments
    /// * `config` - Optional configuration (uses defaults if None)
    ///
    /// # Returns
    /// A new `DataProcessor` instance or an error if configuration is invalid
    ///
    /// # Errors
    /// Returns `BenchmarkError` if configuration validation fails
    pub fn new(config: Option<DataProcessorConfig>) -> Result<Self> {
        let config = config.unwrap_or_default();
        config.validate()?;
        
        Ok(Self {
            config,
            template_engine: TemplateEngine::new(),
        })
    }
    
    /// Process a batch of text strings into token sequences.
    ///
    /// Validates, processes, and optionally pads all items in the batch.
    /// More efficient than processing items individually.
    ///
    /// # Arguments
    /// * `data` - Slice of text strings to process
    ///
    /// # Returns
    /// Vector of token sequences (Vec<u32>), one per input string
    ///
    /// # Errors
    /// Returns `BenchmarkError` if:
    /// - Batch is empty (unless skip_empty is enabled)
    /// - Any item fails validation
    pub fn process_batch(&self, data: &[String]) -> Result<Vec<Vec<u32>>> {
        // Validate batch is not empty (unless skip_empty is enabled)
        if !self.config.skip_empty {
            validate_batch_not_empty(data, "data")?;
        }
        
        // Pre-allocate result vector for efficiency
        let mut results = Vec::with_capacity(data.len());
        
        // Process each item in the batch
        for (index, text) in data.iter().enumerate() {
            // Skip empty items if configured to do so
            if self.config.skip_empty && text.is_empty() {
                results.push(Vec::new());
                continue;
            }
            
            // Validate item before processing
            self.validate_item(text, index)?;
            
            // Process the text into tokens
            let processed = self.process_text(text)?;
            results.push(processed);
        }
        
        // Apply padding if configured
        if self.config.padding {
            self.pad_batch(&mut results)?;
        }
        
        Ok(results)
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Private helper methods
    // ═══════════════════════════════════════════════════════════════════════════
    
    /// Validate a single item in the batch.
    fn validate_item(&self, text: &str, index: usize) -> Result<()> {
        validate_non_empty(text, &format!("data[{}]", index))?;
        
        if let Some(max_len) = self.config.max_length {
            validate_length(text, 1, Some(max_len), &format!("data[{}]", index))?;
        }
        
        Ok(())
    }
    
    /// Process a single text string into a token sequence.
    ///
    /// Converts text to bytes (as u32) and applies truncation if needed.
    /// This is a simplified tokenization - in production, you would use
    /// an actual tokenizer.
    ///
    /// # Arguments
    /// * `text` - Input text to process
    ///
    /// # Returns
    /// Vector of token IDs (currently byte values as u32)
    fn process_text(&self, text: &str) -> Result<Vec<u32>> {
        // Convert text to bytes (simplified tokenization)
        // In production, this would use an actual tokenizer
        let mut tokens: Vec<u32> = text
            .as_bytes()
            .iter()
            .map(|&b| b as u32)
            .collect();
        
        // Apply truncation if configured and needed
        if let Some(max_len) = self.config.max_length {
            if self.config.truncation && tokens.len() > max_len {
                tokens.truncate(max_len);
            }
        }
        
        Ok(tokens)
    }
    
    /// Pad all items in a batch to the same length.
    ///
    /// Finds the maximum length in the batch and pads shorter items
    /// with the configured pad token ID.
    ///
    /// # Arguments
    /// * `batch` - Mutable slice of token sequences to pad
    ///
    /// # Returns
    /// Ok(()) on success, error if batch is empty
    fn pad_batch(&self, batch: &mut [Vec<u32>]) -> Result<()> {
        if batch.is_empty() {
            return Ok(());
        }
        
        // Find maximum length in the batch
        let max_len = batch.iter()
            .map(|tokens| tokens.len())
            .max()
            .ok_or_else(|| BenchmarkError::invalid_input("Empty batch"))?;
        
        // Pad each item to max_len
        for item in batch.iter_mut() {
            let pad_len = max_len.saturating_sub(item.len());
            if pad_len > 0 {
                // Use extend with repeat for efficiency
                item.reserve(pad_len);
                item.extend(std::iter::repeat(self.config.pad_token_id).take(pad_len));
            }
        }
        
        Ok(())
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Template operations
    // ═══════════════════════════════════════════════════════════════════════════
    
    /// Format a prompt template with variable substitution.
    ///
    /// Replaces template variables (e.g., `{name}`) with values from the
    /// provided variables map.
    ///
    /// # Arguments
    /// * `template` - Template string with variable placeholders
    /// * `variables` - Map of variable names to their values
    ///
    /// # Returns
    /// Formatted string with variables substituted
    ///
    /// # Errors
    /// Returns `BenchmarkError` if required variables are missing
    pub fn format_prompt(
        &self,
        template: &str,
        variables: &HashMap<String, String>,
    ) -> Result<String> {
        self.template_engine.format(template, variables)
    }
    
    /// Format a batch of prompts using the same template.
    ///
    /// More efficient than calling `format_prompt` multiple times as it
    /// can reuse template parsing.
    ///
    /// # Arguments
    /// * `template` - Template string with variable placeholders
    /// * `variables_batch` - Vector of variable maps, one per prompt
    ///
    /// # Returns
    /// Vector of formatted strings
    pub fn format_prompt_batch(
        &self,
        template: &str,
        variables_batch: &[HashMap<String, String>],
    ) -> Result<Vec<String>> {
        self.template_engine.format_batch(template, variables_batch)
    }
    
    /// Extract variable names required by a template.
    ///
    /// Parses the template and returns a list of all variable names
    /// that need to be provided for formatting.
    ///
    /// # Arguments
    /// * `template` - Template string to analyze
    ///
    /// # Returns
    /// Vector of required variable names
    pub fn get_template_variables(&self, template: &str) -> Result<Vec<String>> {
        self.template_engine.get_variables(template)
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Validation and configuration
    // ═══════════════════════════════════════════════════════════════════════════
    
    /// Validate a batch of data strings.
    ///
    /// Checks that all items meet the configured constraints (length,
    /// non-empty, etc.) without actually processing them.
    ///
    /// # Arguments
    /// * `data` - Slice of text strings to validate
    ///
    /// # Returns
    /// Ok(()) if all items are valid, error otherwise
    pub fn validate_batch(&self, data: &[String]) -> Result<()> {
        if !self.config.skip_empty {
            validate_batch_not_empty(data, "data")?;
        }
        
        for (index, text) in data.iter().enumerate() {
            // Skip empty items if configured to do so
            if self.config.skip_empty && text.is_empty() {
                continue;
            }
            
            // Validate non-empty
            validate_non_empty(text, &format!("data[{}]", index))?;
            
            // Validate length constraints
            if let Some(max_len) = self.config.max_length {
                if text.len() > max_len && !self.config.truncation {
                    return Err(BenchmarkError::invalid_input(
                        format!(
                            "Text at index {} exceeds max_length {} and truncation is disabled",
                            index, max_len
                        )
                    ));
                }
            }
        }
        
        Ok(())
    }
    
    /// Get the current configuration.
    pub fn config(&self) -> &DataProcessorConfig {
        &self.config
    }
    
    /// Update the configuration.
    ///
    /// # Arguments
    /// * `config` - New configuration to apply
    ///
    /// # Errors
    /// Returns `BenchmarkError` if configuration validation fails
    pub fn set_config(&mut self, config: DataProcessorConfig) -> Result<()> {
        config.validate()?;
        self.config = config;
        Ok(())
    }
    
    /// Clear the template engine's internal cache.
    ///
    /// Useful for freeing memory or forcing template re-parsing.
    pub fn clear_template_cache(&self) {
        self.template_engine.clear_cache();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_process_batch() {
        let processor = DataProcessor::new(None).unwrap();
        let data = vec!["hello".to_string(), "world".to_string()];
        let result = processor.process_batch(&data).unwrap();
        assert_eq!(result.len(), 2);
    }
    
    #[test]
    fn test_format_prompt() {
        let processor = DataProcessor::new(None).unwrap();
        let mut vars = HashMap::new();
        vars.insert("name".to_string(), "Alice".to_string());
        
        let template = "Hello, {name}!";
        let result = processor.format_prompt(template, &vars).unwrap();
        assert_eq!(result, "Hello, Alice!");
    }
    
    #[test]
    fn test_pad_batch() {
        let processor = DataProcessor::new(None).unwrap();
        let mut batch = vec![
            vec![1, 2, 3],
            vec![4, 5],
        ];
        processor.pad_batch(&mut batch).unwrap();
        assert_eq!(batch[0].len(), 3);
        assert_eq!(batch[1].len(), 3);
        assert_eq!(batch[1][2], 0);
    }
}


