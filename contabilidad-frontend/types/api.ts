// Tipos para las solicitudes de la API

export interface CalcularImpuestosRequest {
  regimen: string;
  tipo_impuesto: string;
  datos: Record<string, any>;
  priority?: number;
}

export interface AsesoriaFiscalRequest {
  pregunta: string;
  contexto?: Record<string, any>;
  priority?: number;
}

export interface GuiaFiscalRequest {
  tema: string;
  nivel_detalle?: string;
  priority?: number;
}

export interface TramiteSATRequest {
  tipo_tramite: string;
  detalles?: Record<string, any>;
  priority?: number;
}

export interface AyudaDeclaracionRequest {
  tipo_declaracion: string;
  periodo: string;
  datos?: Record<string, any>;
  priority?: number;
}

// Tipos para las respuestas de la API

export interface TaskSubmittedResponse {
  task_id: string;
  status: string;
}

export interface TaskStatus {
  id: string;
  service_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  priority: number;
}

export interface TaskResult {
  resultado: string;
  tokens_used?: number;
  model?: string;
  tiempo_calculo?: string;
  [key: string]: any;
}

export interface HealthCheckResponse {
  status: string;
  agent_running: boolean;
}














