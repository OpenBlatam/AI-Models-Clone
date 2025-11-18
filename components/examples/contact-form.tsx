'use client';

import { useState } from 'react';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useFormValidation } from '@/hooks/use-form-validation';
import { toast } from 'react-hot-toast';
import { Send, Loader2, CheckCircle } from 'lucide-react';

// Contact form validation schema
const contactSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters'),
  email: z.string()
    .email('Please enter a valid email address'),
  subject: z.string()
    .min(5, 'Subject must be at least 5 characters')
    .max(200, 'Subject must be less than 200 characters'),
  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(1000, 'Message must be less than 1000 characters'),
});

type ContactFormData = z.infer<typeof contactSchema>;

const initialValues: ContactFormData = {
  name: '',
  email: '',
  subject: '',
  message: '',
};

export function ContactForm() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const {
    values,
    errors,
    isValid,
    isSubmitting,
    touched,
    setFieldValue,
    setFieldTouched,
    getFieldError,
    isFieldTouched,
    hasFieldError,
    handleSubmit,
    resetForm,
  } = useFormValidation(contactSchema, initialValues);

  const onSubmit = async (data: ContactFormData) => {
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to send message');
      }

      const result = await response.json();
      toast.success(result.message);
      setIsSubmitted(true);
      resetForm();
    } catch (error) {
      console.error('Contact form error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to send message');
    }
  };

  const handleFieldChange = (field: keyof ContactFormData, value: string) => {
    setFieldValue(field, value);
    
    // Clear error when user starts typing
    if (hasFieldError(field)) {
      const validation = contactSchema.pick({ [field]: true }).safeParse({ [field]: value });
      if (validation.success) {
        // Remove the field error
        // This would require updating the hook to support removing individual errors
      }
    }
  };

  const handleFieldBlur = (field: keyof ContactFormData) => {
    setFieldTouched(field, true);
  };

  if (isSubmitted) {
    return (
      <Card className="max-w-md mx-auto text-center">
        <CardContent className="pt-6">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Message Sent!</h3>
          <p className="text-muted-foreground mb-4">
            Thank you for your message. We will get back to you soon!
          </p>
          <Button onClick={() => setIsSubmitted(false)}>
            Send Another Message
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Contact Us</CardTitle>
        <CardDescription>
          Have a question or want to get in touch? Send us a message and we'll respond as soon as possible.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={(e) => e.preventDefault()} className="space-y-6">
          {/* Name Field */}
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium">
              Name *
            </label>
            <Input
              id="name"
              type="text"
              placeholder="Your full name"
              value={values.name}
              onChange={(e) => handleFieldChange('name', e.target.value)}
              onBlur={() => handleFieldBlur('name')}
              error={isFieldTouched('name') && hasFieldError('name')}
              className={hasFieldError('name') ? 'border-destructive' : ''}
            />
            {isFieldTouched('name') && hasFieldError('name') && (
              <p className="text-sm text-destructive">{getFieldError('name')}</p>
            )}
          </div>

          {/* Email Field */}
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Email *
            </label>
            <Input
              id="email"
              type="email"
              placeholder="your.email@example.com"
              value={values.email}
              onChange={(e) => handleFieldChange('email', e.target.value)}
              onBlur={() => handleFieldBlur('email')}
              error={isFieldTouched('email') && hasFieldError('email')}
              className={hasFieldError('email') ? 'border-destructive' : ''}
            />
            {isFieldTouched('email') && hasFieldError('email') && (
              <p className="text-sm text-destructive">{getFieldError('email')}</p>
            )}
          </div>

          {/* Subject Field */}
          <div className="space-y-2">
            <label htmlFor="subject" className="text-sm font-medium">
              Subject *
            </label>
            <Input
              id="subject"
              type="text"
              placeholder="What is this about?"
              value={values.subject}
              onChange={(e) => handleFieldChange('subject', e.target.value)}
              onBlur={() => handleFieldBlur('subject')}
              error={isFieldTouched('subject') && hasFieldError('subject')}
              className={hasFieldError('subject') ? 'border-destructive' : ''}
            />
            {isFieldTouched('subject') && hasFieldError('subject') && (
              <p className="text-sm text-destructive">{getFieldError('subject')}</p>
            )}
          </div>

          {/* Message Field */}
          <div className="space-y-2">
            <label htmlFor="message" className="text-sm font-medium">
              Message *
            </label>
            <textarea
              id="message"
              rows={5}
              placeholder="Tell us more about your inquiry..."
              value={values.message}
              onChange={(e) => handleFieldChange('message', e.target.value)}
              onBlur={() => handleFieldBlur('message')}
              className={`w-full px-3 py-2 border rounded-md text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent ${
                hasFieldError('message') ? 'border-destructive focus:ring-destructive' : ''
              }`}
            />
            {isFieldTouched('message') && hasFieldError('message') && (
              <p className="text-sm text-destructive">{getFieldError('message')}</p>
            )}
          </div>

          {/* Honeypot field for spam protection */}
          <input
            type="text"
            name="honeypot"
            style={{ display: 'none' }}
            tabIndex={-1}
            autoComplete="off"
          />

          {/* Submit Button */}
          <Button
            type="submit"
            onClick={() => handleSubmit(onSubmit)}
            disabled={!isValid || isSubmitting}
            className="w-full"
            size="lg"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Send Message
              </>
            )}
          </Button>

          {/* Form Status */}
          {!isValid && (
            <p className="text-sm text-muted-foreground text-center">
              Please fill in all required fields correctly.
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}





