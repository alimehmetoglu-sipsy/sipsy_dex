// API-related types for HTTP requests and responses

import { UUID, Timestamp, PaginatedResponse, APIResponse, APIError } from './common';

// HTTP method types
export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';

// API endpoint configuration
export interface APIEndpoint {
  method: HTTPMethod;
  path: string;
  description: string;
  authentication: boolean;
  permissions?: string[];
  parameters?: APIParameter[];
  requestBody?: APIRequestBody;
  responses: APIResponse[];
}

export interface APIParameter {
  name: string;
  in: 'path' | 'query' | 'header';
  type: 'string' | 'number' | 'boolean' | 'array';
  required: boolean;
  description: string;
  example?: unknown;
  enum?: string[];
}

export interface APIRequestBody {
  contentType: string;
  schema: string;
  example?: unknown;
  description: string;
}

export interface APIResponseDefinition {
  statusCode: number;
  description: string;
  contentType: string;
  schema?: string;
  example?: unknown;
}

// Request/Response headers
export interface APIHeaders {
  'Content-Type'?: string;
  'Authorization'?: string;
  'X-Request-ID'?: string;
  'X-API-Version'?: string;
  'X-Rate-Limit-Remaining'?: string;
  'X-Rate-Limit-Reset'?: string;
  [key: string]: string | undefined;
}

// Rate limiting
export interface RateLimit {
  limit: number;
  remaining: number;
  reset: number;
  window: number;
}

export interface RateLimitError extends APIError {
  rateLimit: RateLimit;
}

// File upload types
export interface FileUpload {
  id: UUID;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  path: string;
  url?: string;
  uploadedBy: UUID;
  createdAt: Timestamp;
}

export interface FileUploadRequest {
  file: File | Buffer;
  filename?: string;
  description?: string;
  tags?: string[];
}

export interface BulkUploadRequest {
  files: FileUploadRequest[];
  metadata?: Record<string, unknown>;
}

export interface BulkUploadResponse {
  uploads: FileUpload[];
  errors: Array<{
    filename: string;
    error: string;
  }>;
}

// Search and filtering
export interface SearchRequest {
  query: string;
  filters?: Record<string, unknown>;
  sort?: {
    field: string;
    direction: 'asc' | 'desc';
  };
  page?: number;
  limit?: number;
}

export interface SearchResponse<T> extends PaginatedResponse<T> {
  query: string;
  filters: Record<string, unknown>;
  aggregations?: Record<string, unknown>;
  suggestions?: string[];
}

// Export/Import types
export interface ExportRequest {
  format: 'json' | 'csv' | 'xlsx' | 'pdf';
  filters?: Record<string, unknown>;
  fields?: string[];
  dateRange?: {
    from: Timestamp;
    to: Timestamp;
  };
}

export interface ExportResponse {
  id: UUID;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  format: string;
  filename: string;
  downloadUrl?: string;
  expiresAt: Timestamp;
  recordCount?: number;
  fileSize?: number;
  error?: string;
  createdAt: Timestamp;
}

export interface ImportRequest {
  file: FileUpload;
  format: 'json' | 'csv' | 'xlsx';
  mapping?: Record<string, string>;
  options?: {
    skipHeader?: boolean;
    delimiter?: string;
    validateOnly?: boolean;
    upsert?: boolean;
  };
}

export interface ImportResponse {
  id: UUID;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  filename: string;
  totalRecords: number;
  processedRecords: number;
  successfulRecords: number;
  failedRecords: number;
  errors: Array<{
    row: number;
    field?: string;
    message: string;
  }>;
  validationErrors?: Array<{
    field: string;
    message: string;
  }>;
  createdAt: Timestamp;
  completedAt?: Timestamp;
}

// Batch operations
export interface BatchRequest<T> {
  operations: Array<{
    operation: 'create' | 'update' | 'delete';
    data: T;
    id?: UUID;
  }>;
  continueOnError?: boolean;
}

export interface BatchResponse<T> {
  results: Array<{
    operation: 'create' | 'update' | 'delete';
    success: boolean;
    data?: T;
    error?: string;
  }>;
  summary: {
    total: number;
    successful: number;
    failed: number;
  };
}

// Webhook types
export interface Webhook {
  id: UUID;
  name: string;
  url: string;
  events: string[];
  secret: string;
  enabled: boolean;
  retryAttempts: number;
  retryDelay: number;
  lastDelivery?: Timestamp;
  lastStatus?: number;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface WebhookEvent {
  id: UUID;
  webhookId: UUID;
  event: string;
  payload: Record<string, unknown>;
  status: 'pending' | 'delivered' | 'failed' | 'retrying';
  attempts: number;
  lastAttempt?: Timestamp;
  responseStatus?: number;
  responseBody?: string;
  error?: string;
  createdAt: Timestamp;
}

export interface WebhookCreateRequest {
  name: string;
  url: string;
  events: string[];
  secret?: string;
  enabled?: boolean;
  retryAttempts?: number;
  retryDelay?: number;
}

export interface WebhookUpdateRequest {
  name?: string;
  url?: string;
  events?: string[];
  secret?: string;
  enabled?: boolean;
  retryAttempts?: number;
  retryDelay?: number;
}

// API versioning
export interface APIVersion {
  version: string;
  status: 'current' | 'deprecated' | 'retired';
  releaseDate: Timestamp;
  deprecationDate?: Timestamp;
  retirementDate?: Timestamp;
  changelog: string;
  endpoints: APIEndpoint[];
}

// OpenAPI specification
export interface OpenAPISpec {
  openapi: string;
  info: {
    title: string;
    version: string;
    description: string;
    contact?: {
      name: string;
      email: string;
      url: string;
    };
    license?: {
      name: string;
      url: string;
    };
  };
  servers: Array<{
    url: string;
    description: string;
  }>;
  paths: Record<string, Record<string, APIEndpoint>>;
  components: {
    schemas: Record<string, unknown>;
    securitySchemes: Record<string, unknown>;
  };
  security: Array<Record<string, string[]>>;
}