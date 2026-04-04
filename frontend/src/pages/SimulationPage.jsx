import { useState } from 'react'
import InfoPanel from '../components/InfoPanel'
import SectionHeader from '../components/SectionHeader'
import { metalsApi } from '../services/api'
import { formatCurrency, formatDate, metalLabels } from '../utils/formatters'

const initialForm = {
  user_name: 'Ogrenci',
  metal_type: 'XAU',
  amount_try: '',
  start_date: '',
}

function SimulationPage() {
  const [formData, setFormData] = useState(initialForm)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target
    setFormData((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      setLoading(true)
      setError('')

      const payload = {
        ...formData,
        amount_try: Number(formData.amount_try),
      }

      const response = await metalsApi.simulatePortfolio(payload)
      setResult(response.data)
    } catch (requestError) {
      setResult(null)
      setError(requestError.response?.data?.detail ?? 'Simülasyon çalıştırılamadı.')
    } finally {
      setLoading(false)
    }
  }

  const summaryItems = result
    ? [
        {
          label: 'Başlangıç Tutarı',
          value: formatCurrency(result.initial_amount),
          description: `${metalLabels[result.metal_type]} için seçilen başlangıç yatırımı`,
        },
        {
          label: 'Güncel Değer',
          value: formatCurrency(result.final_amount),
          description: `${formatDate(result.end_date)} tarihine göre güncel portföy değeri`,
        },
        {
          label: 'Kar / Zarar',
          value: formatCurrency(result.profit_loss),
          description: 'Pozitif değer karı, negatif değer zararı gösterir',
        },
      ]
    : []

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Simülasyon"
        title="Yatırımını geçmiş bir tarihten bugüne simüle et"
        description="Kullanıcı adı, maden türü, tutar ve başlangıç tarihi bilgilerini gir. Sistem backend'deki risk motorunu çağırarak kar/zarar ve %95 VaR sonucunu döndürsün."
      />

      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft"
        >
          <div>
            <label htmlFor="user_name" className="mb-2 block text-sm font-semibold text-slate-700">
              Kullanıcı Adı
            </label>
            <input
              id="user_name"
              name="user_name"
              value={formData.user_name}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
              placeholder="Ad Soyad"
              required
            />
          </div>

          <div>
            <label htmlFor="metal_type" className="mb-2 block text-sm font-semibold text-slate-700">
              Maden Türü
            </label>
            <select
              id="metal_type"
              name="metal_type"
              value={formData.metal_type}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
            >
              <option value="XAU">Altın (XAU)</option>
              <option value="XAG">Gümüş (XAG)</option>
            </select>
          </div>

          <div>
            <label htmlFor="amount_try" className="mb-2 block text-sm font-semibold text-slate-700">
              Yatırım Tutarı (TL)
            </label>
            <input
              id="amount_try"
              name="amount_try"
              type="number"
              min="0"
              step="0.01"
              value={formData.amount_try}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
              placeholder="10000"
              required
            />
          </div>

          <div>
            <label htmlFor="start_date" className="mb-2 block text-sm font-semibold text-slate-700">
              Başlangıç Tarihi
            </label>
            <input
              id="start_date"
              name="start_date"
              type="date"
              value={formData.start_date}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? 'Simülasyon hesaplanıyor...' : 'Simülasyonu Çalıştır'}
          </button>

          {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>}
        </form>

        <div className="space-y-6 rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft">
          <div className="rounded-[1.5rem] bg-slate-950 p-6 text-white">
            <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Risk Sonucu</p>
            <p className="mt-4 text-3xl font-bold">{result ? formatCurrency(result.var_95) : '-'}</p>
            <p className="mt-2 text-sm text-slate-300">%95 Historical VaR değeri</p>
          </div>

          {result ? (
            <div className="space-y-6">
              <InfoPanel items={summaryItems} />
              <div className="rounded-3xl bg-slate-50 p-5 text-sm leading-7 text-slate-700">
                {metalLabels[result.metal_type]} yatırımı, <strong>{formatDate(result.start_date)}</strong> tarihinden{' '}
                <strong>{formatDate(result.end_date)}</strong> tarihine kadar backend'deki risk hesaplayıcısıyla değerlendirildi.
              </div>
            </div>
          ) : (
            <div className="rounded-3xl border border-dashed border-slate-300 p-6 text-sm leading-7 text-slate-600">
              Formu doldurup simülasyonu başlattığında burada güncel değer, kar/zarar ve VaR özetini göreceksin.
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default SimulationPage
