import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000/api' : '/api');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for clear error extraction
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';
    return Promise.reject(new Error(message));
  }
);

// --- Health ---
export const checkHealth = () => api.get('/health');

// --- Patients ---
export const getPatients = (params) => api.get('/patients', { params });
export const getPatient = (id) => api.get(`/patients/${id}`);
export const createPatient = (data) => api.post('/patients', data);
export const updatePatient = (id, data) => api.put(`/patients/${id}`, data);
export const deletePatient = (id) => api.delete(`/patients/${id}`);
export const getPatientJourney = (id) => api.get(`/patients/${id}/journey`);

// --- Doctors & Departments ---
export const getDoctors = (params) => api.get('/doctors', { params });
export const getDepartments = () => api.get('/departments');

// --- Appointments ---
export const getAppointments = (params) => api.get('/appointments', { params });
export const createAppointment = (data) => api.post('/appointments', data);
export const updateAppointment = (id, data) => api.put(`/appointments/${id}`, data);
export const deleteAppointment = (id) => api.delete(`/appointments/${id}`);

// --- Consultations & Lab Tests ---
export const getConsultations = (params) => api.get('/consultations', { params });
export const getConsultation = (id) => api.get(`/consultations/${id}`);
export const createConsultation = (data) => api.post('/consultations', data);
export const getMedicines = () => api.get('/consultations/medicines');
export const getTechnicians = () => api.get('/consultations/technicians');
export const getLabTests = (params) => api.get('/labtests', { params });
export const updateLabTest = (id, data) => api.put(`/labtests/${id}`, data);

// --- Billing & Claims ---
export const getBills = (params) => api.get('/bills', { params });
export const createBill = (data) => api.post('/bills', data);
export const updateBill = (id, data) => api.put(`/bills/${id}`, data);
export const deleteBill = (id) => api.delete(`/bills/${id}`);
export const updateClaim = (id, data) => api.put(`/claims/${id}`, data);
export const getInsuranceCompanies = () => api.get('/insurance-companies');
export const getPatientBillingReport = () => api.get('/reports/patient-billing');

// --- Dashboard ---
export const getDashboardSummary = () => api.get('/dashboard/summary');
export const getDashboardBilling = () => api.get('/dashboard/billing');
export const getDashboardClaims = () => api.get('/dashboard/payments');
export const getDashboardDoctors = () => api.get('/dashboard/doctors');

// --- Query Console ---
export const getQueries = () => api.get('/queries');
export const runNamedQuery = (name, id) => api.get(`/queries/${name}`, { params: id ? { id } : {} });

export default api;
