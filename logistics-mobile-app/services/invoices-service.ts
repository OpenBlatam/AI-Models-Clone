import { apiClient } from '@/utils/api-client';
import { InvoiceResponse } from '@/types';

export const invoicesService = {
  createInvoice: async (shipmentId: string, data: { amount: number; currency?: string }): Promise<InvoiceResponse> => {
    return apiClient.post<InvoiceResponse>('/invoices', { shipment_id: shipmentId, ...data });
  },

  getInvoices: async (): Promise<InvoiceResponse[]> => {
    return apiClient.get<InvoiceResponse[]>('/invoices');
  },

  getInvoice: async (invoiceId: string): Promise<InvoiceResponse> => {
    return apiClient.get<InvoiceResponse>(`/invoices/${invoiceId}`);
  },

  getInvoicesByShipment: async (shipmentId: string): Promise<InvoiceResponse[]> => {
    return apiClient.get<InvoiceResponse[]>(`/invoices/shipment/${shipmentId}`);
  },
};


