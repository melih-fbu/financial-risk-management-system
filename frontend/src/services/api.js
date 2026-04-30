import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const metalsApi = {
  getAllPrices: () => api.get('/metals/prices'),
  getPricesByMetal: (metalType) => api.get(`/metals/prices/${metalType}`),
  simulatePortfolio: (payload) => api.post('/metals/simulate', payload),
  getVarByMetal: (metalType) => api.get(`/metals/var/${metalType}`),
}

export const reportsApi = {
  getCustomerSummary: () => api.get('/reports/customer-summary'),
  compareMetals: (payload) => api.post('/reports/compare-metals', payload),
  getRiskSummary: (customerId) => api.get(`/reports/risk-summary/${customerId}`),
  getMetalAnalysis: (metalType) => api.get(`/reports/metal-analysis/${metalType}`),
  runMonteCarlo: (payload) => api.post('/reports/monte-carlo', payload),
  predictMetal: (metalType, daysAhead) => api.get(`/reports/predict/${metalType}?days_ahead=${daysAhead}`),
  getSignal: (metalType) => api.get(`/reports/signal/${metalType}`),
}

export default api
