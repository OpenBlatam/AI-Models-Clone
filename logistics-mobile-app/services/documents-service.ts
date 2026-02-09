import { apiClient } from '@/utils/api-client';
import { DocumentResponse, DocumentRequest } from '@/types';
import * as FileSystem from 'expo-file-system';

export const documentsService = {
  uploadDocument: async (request: DocumentRequest): Promise<DocumentResponse> => {
    const formData = new FormData();
    formData.append('shipment_id', request.shipment_id);
    formData.append('document_type', request.document_type);
    formData.append('file', {
      uri: request.file.uri,
      type: request.file.type,
      name: request.file.name,
    } as unknown as Blob);

    return apiClient.upload<DocumentResponse>('/documents', formData);
  },

  getDocument: async (documentId: string): Promise<DocumentResponse> => {
    return apiClient.get<DocumentResponse>(`/documents/${documentId}`);
  },

  getDocumentsByShipment: async (shipmentId: string): Promise<DocumentResponse[]> => {
    return apiClient.get<DocumentResponse[]>(`/documents/shipment/${shipmentId}`);
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    return apiClient.delete<void>(`/documents/${documentId}`);
  },

  downloadDocument: async (document: DocumentResponse): Promise<string> => {
    if (!document.url) {
      throw new Error('Document URL not available');
    }
    const fileUri = `${FileSystem.documentDirectory}${document.file_name}`;
    const downloadResult = await FileSystem.downloadAsync(document.url, fileUri);
    return downloadResult.uri;
  },
};


