import { apiClient } from '@/utils/api-client';
import { ContainerRequest, ContainerResponse, ContainerStatus } from '@/types';

export const containersService = {
  createContainer: async (request: ContainerRequest): Promise<ContainerResponse> => {
    return apiClient.post<ContainerResponse>('/forwarding/containers', request);
  },

  getContainer: async (containerId: string): Promise<ContainerResponse> => {
    return apiClient.get<ContainerResponse>(`/forwarding/containers/${containerId}`);
  },

  getContainersByShipment: async (shipmentId: string): Promise<ContainerResponse[]> => {
    return apiClient.get<ContainerResponse[]>(`/forwarding/containers/shipment/${shipmentId}`);
  },

  updateContainerStatus: async (containerId: string, status: ContainerStatus): Promise<ContainerResponse> => {
    return apiClient.patch<ContainerResponse>(`/forwarding/containers/${containerId}/status`, { status });
  },
};


