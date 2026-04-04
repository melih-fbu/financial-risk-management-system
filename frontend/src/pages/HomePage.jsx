import { useEffect, useState } from 'react'
import SectionHeader from '../components/SectionHeader'
import StatusCard from '../components/StatusCard'
import { metalsApi } from '../services/api'
import { formatCurrency, getLatestPrices } from '../utils/formatters'

function HomePage() {
  const [prices, setPrices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchPrices() {
      try {
        setLoading(true)
        const response = await metalsApi.getAllPrices()
        setPrices(response.data)
        setError('')
      } catch {
        setError('Fiyat verileri alınamadı. FastAPI servisinin çalıştığını kontrol edin.')
      } finally {
        setLoading(false)
      }
    }

    fetchPrices()
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
        <section className="grid gap-6 md:grid-cols-2">
          <StatusCard metalType="XAU" item={latestPrices.XAU} />
          <StatusCard metalType="XAG" item={latestPrices.XAG} />
        </section>
      )}
    </div>
  )
}

export default HomePage
