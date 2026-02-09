import { StoreType, DesignStyle } from '@/types'

export const STORE_TYPE_LABELS: Record<StoreType, string> = {
  [StoreType.RETAIL]: 'Retail',
  [StoreType.RESTAURANT]: 'Restaurante',
  [StoreType.CAFE]: 'Café',
  [StoreType.BOUTIQUE]: 'Boutique',
  [StoreType.SUPERMARKET]: 'Supermercado',
  [StoreType.PHARMACY]: 'Farmacia',
  [StoreType.ELECTRONICS]: 'Electrónica',
  [StoreType.CLOTHING]: 'Ropa',
  [StoreType.FURNITURE]: 'Muebles',
  [StoreType.OTHER]: 'Otro',
}

export const DESIGN_STYLE_LABELS: Record<DesignStyle, string> = {
  [DesignStyle.MODERN]: 'Moderno',
  [DesignStyle.CLASSIC]: 'Clásico',
  [DesignStyle.MINIMALIST]: 'Minimalista',
  [DesignStyle.INDUSTRIAL]: 'Industrial',
  [DesignStyle.RUSTIC]: 'Rústico',
  [DesignStyle.LUXURY]: 'Lujo',
  [DesignStyle.ECO_FRIENDLY]: 'Ecológico',
  [DesignStyle.VINTAGE]: 'Vintage',
}

export function getStoreTypeLabel(type: StoreType): string {
  return STORE_TYPE_LABELS[type] || type
}

export function getDesignStyleLabel(style: DesignStyle): string {
  return DESIGN_STYLE_LABELS[style] || style.replace('_', ' ')
}


