import { apiClient } from '@/utils/api-client';
import { InsuranceRequest, InsuranceResponse } from '@/types';

export const insuranceService = {
  createInsurance: async (request: InsuranceRequest): Promise<InsuranceResponse> => {
    return apiClient.post<InsuranceResponse>('/insurance', request);
  },

  getInsurance: async (insuranceId: string): Promise<InsuranceResponse> => {
    return apiClient.get<InsuranceResponse>(`/insurance/${insuranceId}`);
  },

  getInsuranceByShipment: async (shipmentId: string): Promise<InsuranceResponse> => {
    return apiClient.get<InsuranceResponse>(`/insurance/shipment/${shipmentId}`);
  },
};


