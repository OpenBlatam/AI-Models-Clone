import * as FileSystem from 'expo-file-system';
import { VALIDATION } from '@/constants';

// File Utilities

export function getFileExtension(filename: string): string {
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
}

export function getFileName(path: string): string {
  return path.split('/').pop() || path;
}

export function getFileMimeType(filename: string): string {
  const extension = getFileExtension(filename);
  const mimeTypes: Record<string, string> = {
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    gif: 'image/gif',
    webp: 'image/webp',
    pdf: 'application/pdf',
    doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    txt: 'text/plain',
    csv: 'text/csv',
  };
  
  return mimeTypes[extension] || 'application/octet-stream';
}

export function isValidImageFile(filename: string): boolean {
  const extension = getFileExtension(filename);
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
  return imageExtensions.includes(extension);
}

export function isValidDocumentFile(filename: string): boolean {
  const extension = getFileExtension(filename);
  const documentExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'];
  return documentExtensions.includes(extension);
}

export async function getFileSize(uri: string): Promise<number> {
  try {
    const fileInfo = await FileSystem.getInfoAsync(uri);
    if (fileInfo.exists && 'size' in fileInfo) {
      return fileInfo.size;
    }
    return 0;
  } catch {
    return 0;
  }
}

export async function fileExists(uri: string): Promise<boolean> {
  try {
    const fileInfo = await FileSystem.getInfoAsync(uri);
    return fileInfo.exists;
  } catch {
    return false;
  }
}

export async function deleteFile(uri: string): Promise<boolean> {
  try {
    const fileInfo = await FileSystem.getInfoAsync(uri);
    if (fileInfo.exists) {
      await FileSystem.deleteAsync(uri, { idempotent: true });
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

export function isValidFileSize(size: number, maxSize: number = VALIDATION.FILE_SIZE.MAX_DOCUMENT): boolean {
  return size <= maxSize;
}

export function createFormData(fileUri: string, fieldName: string = 'file'): FormData {
  const formData = new FormData();
  const filename = getFileName(fileUri);
  const mimeType = getFileMimeType(filename);
  
  formData.append(fieldName, {
    uri: fileUri,
    type: mimeType,
    name: filename,
  } as any);
  
  return formData;
}

