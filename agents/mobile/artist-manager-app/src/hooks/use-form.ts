import { useForm as useReactHookForm, UseFormReturn } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useToast } from './use-toast';

interface UseFormOptions<T extends z.ZodType> {
  schema: T;
  defaultValues?: z.infer<T>;
  onSubmit: (data: z.infer<T>) => Promise<void> | void;
  onError?: (error: Error) => void;
}

export function useForm<T extends z.ZodType>({
  schema,
  defaultValues,
  onSubmit,
  onError,
}: UseFormOptions<T>): UseFormReturn<z.infer<T>> & {
  handleSubmit: () => Promise<void>;
} {
  const toast = useToast();
  const form = useReactHookForm<z.infer<T>>({
    resolver: zodResolver(schema),
    defaultValues: defaultValues as z.infer<T>,
    mode: 'onChange',
  });

  const handleSubmit = async () => {
    try {
      const isValid = await form.trigger();
      if (!isValid) {
        toast.showError('Please fix the errors in the form');
        return;
      }

      const data = form.getValues();
      await onSubmit(data);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      toast.showError(errorMessage);
      onError?.(error instanceof Error ? error : new Error(errorMessage));
    }
  };

  return {
    ...form,
    handleSubmit,
  };
}


