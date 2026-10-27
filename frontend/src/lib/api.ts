const API_BASE = typeof window !== 'undefined' ? '' : (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000');

async function fetchJSON<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Health
  getHealth: () => fetchJSON<{ status: string; app: string; environment: string; ai_engine: string; simulation_mode: boolean }>('/api/health'),
  getReady: () => fetchJSON<{ status: string; database: string; calendar_integration: string; weather_service: string }>('/api/ready'),
  seedDatabase: () => fetchJSON<{ status: string; message: string }>('/api/seed', { method: 'POST' }),

  // Intake & AI Agent
  analyzeIntake: (data: {
    message: string;
    customer_name?: string;
    customer_phone?: string;
    vehicle_make?: string;
    vehicle_model?: string;
    vehicle_year?: number;
  }) => fetchJSON<any>('/api/requests/intake', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  createServiceRequest: (data: any) => fetchJSON<any>('/api/requests', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  listServiceRequests: (status?: string) => {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return fetchJSON<any[]>(`/api/requests${query}`);
  },

  getServiceRequestDetail: (id: number) => fetchJSON<any>(`/api/requests/${id}`),

  submitClarification: (id: number, message: string) => fetchJSON<any>(`/api/requests/${id}/messages`, {
    method: 'POST',
    body: JSON.stringify({ request_id: id, message, sender_type: 'customer' }),
  }),

  // Work Orders
  createWorkOrder: (data: any) => fetchJSON<any>('/api/work-orders', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  listWorkOrders: (status?: string) => {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return fetchJSON<any[]>(`/api/work-orders${query}`);
  },

  getWorkOrderDetail: (id: number) => fetchJSON<any>(`/api/work-orders/${id}`),

  updateWorkOrder: (id: number, data: any) => fetchJSON<any>(`/api/work-orders/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),

  // Scheduling & Availability
  getAvailability: (serviceType: string, targetDate: string, durationMinutes: number = 60) =>
    fetchJSON<any[]>(`/api/availability?service_type=${encodeURIComponent(serviceType)}&target_date=${encodeURIComponent(targetDate)}&duration_minutes=${durationMinutes}`),

  confirmAppointment: (data: {
    work_order_id: number;
    bay_id: number;
    mechanic_id: number;
    start_at: string;
    idempotency_key: string;
  }) => fetchJSON<any>('/api/appointments/confirm', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  listAppointments: () => fetchJSON<any[]>('/api/appointments'),

  // Inventory
  getParts: () => fetchJSON<any[]>('/api/inventory/parts'),
  recordMovement: (data: { part_id: number; quantity_delta: number; reason: string; work_order_id?: number }) =>
    fetchJSON<any>('/api/inventory/movements', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  listMovements: () => fetchJSON<any[]>('/api/inventory/movements'),

  // Estimates
  createEstimate: (data: { work_order_id: number; parts_included?: any[]; labor_hours?: number }) =>
    fetchJSON<any>('/api/estimates', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  approveEstimate: (id: number, approvedBy: string, notes?: string) =>
    fetchJSON<any>(`/api/estimates/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approved_by: approvedBy, notes }),
    }),

  // Integrations
  getWeather: (serviceType?: string) => {
    const q = serviceType ? `?service_type=${encodeURIComponent(serviceType)}` : '';
    return fetchJSON<any>(`/api/integrations/weather${q}`);
  },

  syncCalendar: (appointmentId: number, forceFailure: boolean = false) =>
    fetchJSON<any>(`/api/integrations/calendar/sync?appointment_id=${appointmentId}&force_failure=${forceFailure}`, {
      method: 'POST',
    }),

  // Analytics, Audit & Automation
  getAnalyticsSummary: () => fetchJSON<any>('/api/analytics/summary'),
  getAuditEvents: (limit: number = 50) => fetchJSON<any[]>(`/api/audit-events?limit=${limit}`),
  runAutomation: () => fetchJSON<any>('/api/automation/run', { method: 'POST' }),
  listAutomationJobs: () => fetchJSON<any[]>('/api/automation/jobs'),

  // Vehicle Owner Customer Portal & Email Notifications
  sendAuthCode: (email: string) => fetchJSON<any>('/api/customer/auth/send-code', {
    method: 'POST',
    body: JSON.stringify({ email }),
  }),

  verifyAuthCode: (email: string, code: string) => fetchJSON<any>('/api/customer/auth/verify-code', {
    method: 'POST',
    body: JSON.stringify({ email, code }),
  }),

  getCustomerGarage: (email: string) => fetchJSON<any>(`/api/customer/garage?email=${encodeURIComponent(email)}`),

  customerApproveEstimate: (estimateId: number, customerName?: string, notes?: string) =>
    fetchJSON<any>(`/api/customer/estimates/${estimateId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ customer_name: customerName, notes }),
    }),

  getEmailInbox: (email?: string) => {
    const q = email ? `?email=${encodeURIComponent(email)}` : '';
    return fetchJSON<any[]>(`/api/customer/notifications/inbox${q}`);
  },
};
