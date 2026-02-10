//! Prompt Template Engine
//!
//! Advanced template engine for prompt formatting with validation and caching.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use crate::error::{Result, BenchmarkError};
use super::validators::validate_template;

/// Template engine with caching.
pub struct TemplateEngine {
    cache: Arc<Mutex<HashMap<String, ParsedTemplate>>>,
}

/// Parsed template structure.
#[derive(Debug, Clone)]
struct ParsedTemplate {
    variables: Vec<String>,
    parts: Vec<TemplatePart>,
}

#[derive(Debug, Clone)]
enum TemplatePart {
    Literal(String),
    Variable(String),
}

impl TemplateEngine {
    /// Create a new template engine.
    pub fn new() -> Self {
        Self {
            cache: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    
    /// Format template with variables.
    pub fn format(
        &self,
        template: &str,
        variables: &HashMap<String, String>,
    ) -> Result<String> {
        // Validate template
        validate_template(template)?;
        
        // Parse template (with caching)
        let parsed = self.parse_template(template)?;
        
        // Format
        let mut result = String::new();
        for part in &parsed.parts {
            match part {
                TemplatePart::Literal(text) => result.push_str(text),
                TemplatePart::Variable(name) => {
                    let value = variables.get(name)
                        .ok_or_else(|| BenchmarkError::invalid_input(
                            format!("Template variable '{}' not provided", name)
                        ))?;
                    result.push_str(value);
                }
            }
        }
        
        Ok(result)
    }
    
    /// Format batch of templates.
    pub fn format_batch(
        &self,
        template: &str,
        variables_batch: &[HashMap<String, String>],
    ) -> Result<Vec<String>> {
        validate_template(template)?;
        let parsed = self.parse_template(template)?;
        
        variables_batch
            .iter()
            .map(|vars| {
                let mut result = String::new();
                for part in &parsed.parts {
                    match part {
                        TemplatePart::Literal(text) => result.push_str(text),
                        TemplatePart::Variable(name) => {
                            let value = vars.get(name)
                                .ok_or_else(|| BenchmarkError::invalid_input(
                                    format!("Template variable '{}' not provided", name)
                                ))?;
                            result.push_str(value);
                        }
                    }
                }
                Ok(result)
            })
            .collect()
    }
    
    /// Parse template (with caching).
    fn parse_template(&self, template: &str) -> Result<ParsedTemplate> {
        // Check cache
        {
            let cache = self.cache.lock().unwrap();
            if let Some(parsed) = cache.get(template) {
                return Ok(parsed.clone());
            }
        }
        
        // Parse
        let mut parts = Vec::new();
        let mut variables = Vec::new();
        let mut current = String::new();
        let mut in_variable = false;
        
        for ch in template.chars() {
            match ch {
                '{' if !in_variable => {
                    if !current.is_empty() {
                        parts.push(TemplatePart::Literal(current.clone()));
                        current.clear();
                    }
                    in_variable = true;
                }
                '}' if in_variable => {
                    if current.is_empty() {
                        return Err(BenchmarkError::invalid_input(
                            "Empty variable name in template"
                        ));
                    }
                    let var_name = current.clone();
                    if !variables.contains(&var_name) {
                        variables.push(var_name.clone());
                    }
                    parts.push(TemplatePart::Variable(var_name));
                    current.clear();
                    in_variable = false;
                }
                _ => current.push(ch),
            }
        }
        
        if in_variable {
            return Err(BenchmarkError::invalid_input(
                "Unclosed variable in template"
            ));
        }
        
        if !current.is_empty() {
            parts.push(TemplatePart::Literal(current));
        }
        
        let parsed = ParsedTemplate { variables, parts };
        
        // Cache
        {
            let mut cache = self.cache.lock().unwrap();
            cache.insert(template.to_string(), parsed.clone());
        }
        
        Ok(parsed)
    }
    
    /// Get variables required by template.
    pub fn get_variables(&self, template: &str) -> Result<Vec<String>> {
        let parsed = self.parse_template(template)?;
        Ok(parsed.variables)
    }
    
    /// Clear template cache.
    pub fn clear_cache(&self) {
        let mut cache = self.cache.lock().unwrap();
        cache.clear();
    }
}

impl Default for TemplateEngine {
    fn default() -> Self {
        Self::new()
    }
}




