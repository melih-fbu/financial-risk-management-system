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

export default api
