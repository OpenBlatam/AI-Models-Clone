import * as Localization from 'expo-localization';
import { I18n } from 'i18n-js';

// Translations
const translations = {
  en: {
    common: {
      loading: 'Loading...',
      error: 'Error',
      retry: 'Retry',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      create: 'Create',
      close: 'Close',
      confirm: 'Confirm',
    },
    dashboard: {
      title: 'Dashboard',
      upcomingEvents: 'Upcoming Events',
      pendingRoutines: 'Pending Routines',
      criticalProtocols: 'Critical Protocols',
      wardrobeItems: 'Wardrobe Items',
    },
    calendar: {
      title: 'Calendar',
      addEvent: 'Add Event',
      noEvents: 'No events scheduled',
      eventDetails: 'Event Details',
    },
    routines: {
      title: 'Routines',
      addRoutine: 'Add Routine',
      noRoutines: 'No routines defined',
      pending: 'Pending',
      complete: 'Complete',
    },
    wardrobe: {
      title: 'Wardrobe',
      addItem: 'Add Item',
      addOutfit: 'Add Outfit',
      noItems: 'No items in wardrobe',
      noOutfits: 'No outfits created',
    },
    protocols: {
      title: 'Protocols',
      addProtocol: 'Add Protocol',
      noProtocols: 'No protocols defined',
    },
  },
  es: {
    common: {
      loading: 'Cargando...',
      error: 'Error',
      retry: 'Reintentar',
      cancel: 'Cancelar',
      save: 'Guardar',
      delete: 'Eliminar',
      edit: 'Editar',
      create: 'Crear',
      close: 'Cerrar',
      confirm: 'Confirmar',
    },
    dashboard: {
      title: 'Panel',
      upcomingEvents: 'Eventos Próximos',
      pendingRoutines: 'Rutinas Pendientes',
      criticalProtocols: 'Protocolos Críticos',
      wardrobeItems: 'Items de Vestimenta',
    },
    calendar: {
      title: 'Calendario',
      addEvent: 'Agregar Evento',
      noEvents: 'No hay eventos programados',
      eventDetails: 'Detalles del Evento',
    },
    routines: {
      title: 'Rutinas',
      addRoutine: 'Agregar Rutina',
      noRoutines: 'No hay rutinas definidas',
      pending: 'Pendiente',
      complete: 'Completar',
    },
    wardrobe: {
      title: 'Vestimenta',
      addItem: 'Agregar Item',
      addOutfit: 'Agregar Outfit',
      noItems: 'No hay items en el guardarropa',
      noOutfits: 'No hay outfits creados',
    },
    protocols: {
      title: 'Protocolos',
      addProtocol: 'Agregar Protocolo',
      noProtocols: 'No hay protocolos definidos',
    },
  },
};

const i18n = new I18n(translations);
i18n.locale = Localization.locale;
i18n.enableFallback = true;
i18n.defaultLocale = 'en';

export function t(key: string, options?: Record<string, unknown>): string {
  return i18n.t(key, options);
}

export function setLocale(locale: string): void {
  i18n.locale = locale;
}

export function getLocale(): string {
  return i18n.locale;
}

export { i18n };


