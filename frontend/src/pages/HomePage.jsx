import { useEffect, useState } from 'react'
import SectionHeader from '../components/SectionHeader'
import StatusCard from '../components/StatusCard'
import { metalsApi, reportsApi } from '../services/api'
import { formatCurrency, getLatestPrices } from '../utils/formatters'

function HomePage() {
  const [prices, setPrices] = useState([])
  const [riskSummary, setRiskSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchDashboard() {
      try {
        setLoading(true)
        const [pricesResponse, customersResponse] = await Promise.all([
          metalsApi.getAllPrices(),
          reportsApi.getCustomerSummary(),
        ])

        setPrices(pricesResponse.data)

        const firstCustomer = customersResponse.data.find((item) => item.customer_id)
        if (firstCustomer) {
          const riskResponse = await reportsApi.getRiskSummary(firstCustomer.customer_id)
          setRiskSummary(riskResponse.data)
        } else {
          setRiskSummary(null)
        }

        setError('')
      } catch {
        setError('Dashboard verileri alınamadı. FastAPI servisinin çalıştığını kontrol edin.')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  const latestPrices = getLatestPrices(prices)

  return (
    <div className="space-y-8">
      <section className="grid gap-6 rounded-[2rem] border border-white/70 bg-white/70 p-8 shadow-soft lg:grid-cols-[1.3fr_0.7fr]">
        <SectionHeader
          eyebrow="Ana Sayfa"
          title="Altın ve gümüş piyasasını tek ekranda takip et"
          description="Backend'den gelen güncel metal fiyatlarını, son kayıt tarihlerini ve portföy risk akışını sade bir arayüzle izleyebilirsin."
        />

        <div className="rounded-[2rem] bg-slate-950 p-6 text-white">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Toplam görünüm</p>
          <p className="mt-4 text-4xl font-bold">{prices.length}</p>
          <p className="mt-2 text-sm text-slate-300">veri kaydı frontend tarafından işlendi</p>
          <div className="mt-8 space-y-3 text-sm text-slate-300">
            <p>Altın son fiyatı: {formatCurrency(latestPrices.XAU?.price_try)}</p>
            <p>Gümüş son fiyatı: {formatCurrency(latestPrices.XAG?.price_try)}</p>
          </div>
        </div>
      </section>

      {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-rose-700">{error}</div>}

      {loading ? (
        <div className="rounded-3xl border border-slate-200 bg-white/80 p-8 text-slate-600 shadow-soft">
          Güncel fiyat kartları yükleniyor...
        </div>
      ) : (
        <section className="grid gap-6 xl:grid-cols-3">
          <StatusCard metalType="XAU" item={latestPrices.XAU} />
          <StatusCard metalType="XAG" item={latestPrices.XAG} />
          <article className="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-soft">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">Risk Özeti</p>
            {riskSummary ? (
              <div className="mt-6 space-y-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-400">{riskSummary.customer_name}</p>
                  <p className="mt-2 text-3xl font-bold text-slate-950">{formatCurrency(riskSummary.var_95)}</p>
                  <p className="mt-1 text-sm text-slate-500">Toplam %95 VaR</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
                  <p>Toplam yatırım: {formatCurrency(riskSummary.total_investment)}</p>
                  <p>Kar / zarar: {formatCurrency(riskSummary.profit_loss)}</p>
                  <p>BUY işlem sayısı: {riskSummary.buy_transaction_count}</p>
                </div>
                <p className="text-xs leading-6 text-slate-500">
                  Ana sayfada ilk bulunan müşterinin risk özeti gösteriliyor.
                </p>
              </div>
            ) : (
              <div className="mt-6 rounded-2xl border border-dashed border-slate-300 p-4 text-sm leading-6 text-slate-600">
                Risk kartını doldurmak için en az bir müşteri ve BUY işlemi eklenmeli.
              </div>
            )}
          </article>
        </section>
      )}
    </div>
  )
}

export default HomePage
