'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCreateDesign } from '@/hooks/use-designs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StoreType, DesignStyle } from '@/types'
import { Loader2, Store } from 'lucide-react'
import { useToast } from '@/components/ui/toast'
import { getStoreTypeLabel, getDesignStyleLabel } from '@/constants/store-types'

const designSchema = z.object({
  store_name: z.string().min(1, 'El nombre es requerido'),
  store_type: z.nativeEnum(StoreType),
  style_preference: z.nativeEnum(DesignStyle).optional(),
  budget_range: z.string().optional(),
  location: z.string().optional(),
  target_audience: z.string().optional(),
  dimensions: z
    .object({
      width: z.number().positive(),
      length: z.number().positive(),
      height: z.number().positive(),
    })
    .optional(),
  additional_info: z.string().optional(),
})

type DesignFormData = z.infer<typeof designSchema>

export default function DesignPage() {
  const router = useRouter()
  const { showToast } = useToast()
  const { register, handleSubmit, formState: { errors } } = useForm<DesignFormData>({
    resolver: zodResolver(designSchema),
    defaultValues: {
      store_type: StoreType.CAFE,
    },
  })

  const createDesignMutation = useCreateDesign()

  const onSubmit = (data: DesignFormData) => {
    createDesignMutation.mutate(data, {
      onSuccess: (design) => {
        showToast('Diseño generado exitosamente', 'success')
        router.push(`/designs/${design.store_id}`)
      },
      onError: (error: Error) => {
        showToast(error.message || 'Error al generar diseño', 'error')
      },
    })
  }


  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Store className="w-5 h-5" />
            Crear Nuevo Diseño
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Nombre del Local *
              </label>
              <Input {...register('store_name')} />
              {errors.store_name && (
                <p className="text-sm text-red-600 mt-1">
                  {errors.store_name.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Tipo de Tienda *
              </label>
              <Select {...register('store_type')}>
                {Object.values(StoreType).map((type) => (
                  <option key={type} value={type}>
                    {getStoreTypeLabel(type)}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Estilo de Diseño
              </label>
              <Select {...register('style_preference')}>
                <option value="">Seleccionar...</option>
                {Object.values(DesignStyle).map((style) => (
                  <option key={style} value={style}>
                    {getDesignStyleLabel(style)}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Rango de Presupuesto
              </label>
              <Input {...register('budget_range')} placeholder="bajo, medio, alto" />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Ubicación</label>
              <Input {...register('location')} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Audiencia Objetivo
              </label>
              <Input {...register('target_audience')} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Dimensiones (metros)
              </label>
              <div className="grid grid-cols-3 gap-2">
                <Input
                  type="number"
                  step="0.1"
                  placeholder="Ancho"
                  {...register('dimensions.width', { valueAsNumber: true })}
                />
                <Input
                  type="number"
                  step="0.1"
                  placeholder="Largo"
                  {...register('dimensions.length', { valueAsNumber: true })}
                />
                <Input
                  type="number"
                  step="0.1"
                  placeholder="Alto"
                  {...register('dimensions.height', { valueAsNumber: true })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Información Adicional
              </label>
              <Textarea
                {...register('additional_info')}
                rows={4}
                placeholder="Información adicional sobre tu local..."
              />
            </div>

            <Button
              type="submit"
              disabled={createDesignMutation.isPending}
              className="w-full"
            >
              {createDesignMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generando...
                </>
              ) : (
                'Generar Diseño'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

