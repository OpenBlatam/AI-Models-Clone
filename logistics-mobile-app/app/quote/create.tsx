import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useCreateQuote } from '@/hooks/use-quotes';
import { QuoteRequest, TransportationMode } from '@/types';

const quoteSchema = z.object({
  origin_country: z.string().min(1, 'Origin country is required'),
  origin_city: z.string().min(1, 'Origin city is required'),
  destination_country: z.string().min(1, 'Destination country is required'),
  destination_city: z.string().min(1, 'Destination city is required'),
  cargo_description: z.string().min(1, 'Cargo description is required'),
  weight_kg: z.string().refine((val) => !isNaN(parseFloat(val)) && parseFloat(val) > 0, {
    message: 'Valid weight is required',
  }),
  quantity: z.string().refine((val) => !isNaN(parseInt(val)) && parseInt(val) > 0, {
    message: 'Valid quantity is required',
  }),
  transportation_mode: z.nativeEnum(TransportationMode as any),
  insurance_required: z.boolean().default(false),
});

type QuoteFormData = z.infer<typeof quoteSchema>;

export default function CreateQuoteScreen() {
  const router = useRouter();
  const createQuote = useCreateQuote();

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<QuoteFormData>({
    resolver: zodResolver(quoteSchema),
    defaultValues: {
      transportation_mode: TransportationMode.MARITIME,
      insurance_required: false,
    },
  });

  async function onSubmit(data: QuoteFormData) {
    const request: QuoteRequest = {
      origin: {
        country: data.origin_country,
        city: data.origin_city,
      },
      destination: {
        country: data.destination_country,
        city: data.destination_city,
      },
      cargo: {
        description: data.cargo_description,
        weight_kg: parseFloat(data.weight_kg),
        quantity: parseInt(data.quantity),
        unit_type: 'CTN',
        dangerous_goods: false,
        temperature_controlled: false,
      },
      transportation_mode: data.transportation_mode,
      insurance_required: data.insurance_required,
    };

    try {
      const quote = await createQuote.mutateAsync(request);
      router.push(`/quote/${quote.quote_id}`);
    } catch (error) {
      console.error('Error creating quote:', error);
    }
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Create Quote</Text>

        <Controller
          control={control}
          name="origin_country"
          render={({ field: { onChange, onBlur, value } }) => (
            <Input
              label="Origin Country"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={errors.origin_country?.message}
            />
          )}
        />

        <Controller
          control={control}
          name="origin_city"
          render={({ field: { onChange, onBlur, value } }) => (
            <Input
              label="Origin City"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={errors.origin_city?.message}
            />
          )}
        />

        <Controller
          control={control}
          name="destination_country"
          render={({ field: { onChange, onBlur, value } }) => (
            <Input
              label="Destination Country"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={errors.destination_country?.message}
            />
          )}
        />

        <Controller
          control={control}
          name="destination_city"
          render={({ field: { onChange, onBlur, value } }) => (
            <Input
              label="Destination City"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={errors.destination_city?.message}
            />
          )}
        />

        <Controller
          control={control}
          name="cargo_description"
          render={({ field: { onChange, onBlur, value } }) => (
            <Input
              label="Cargo Description"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={errors.cargo_description?.message}
            />
          )}
        />

        <Controller
          control={control}
          name="weight_kg"
          render={({ field: { onChange, onBlur, value } }) => (
            <Input
              label="Weight (kg)"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              keyboardType="numeric"
              error={errors.weight_kg?.message}
            />
          )}
        />

        <Controller
          control={control}
          name="quantity"
          render={({ field: { onChange, onBlur, value } }) => (
            <Input
              label="Quantity"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              keyboardType="numeric"
              error={errors.quantity?.message}
            />
          )}
        />

        <Button
          title="Create Quote"
          onPress={handleSubmit(onSubmit)}
          loading={createQuote.isPending}
          style={styles.submitButton}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 24,
    color: '#000',
  },
  submitButton: {
    marginTop: 24,
  },
});


