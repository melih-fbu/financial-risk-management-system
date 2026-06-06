export const metalLabels = {
  XAU: 'Altın',
  XAG: 'Gümüş',
}

export function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-'
  }

  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 2,
  }).format(Number(value))
}

export function formatDate(value) {
  if (!value) {
    return '-'
  }

  return new Intl.DateTimeFormat('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(value))
}

export function getLatestPrices(prices) {
  return prices.reduce((accumulator, current) => {
    const previous = accumulator[current.metal_type]

    if (!previous || new Date(current.date) > new Date(previous.date)) {
      accumulator[current.metal_type] = current
    }

    return accumulator
  }, {})
}

export function buildHistoryChartData(prices) {
  const rows = prices.reduce((accumulator, item) => {
    const existing = accumulator.get(item.date) ?? { date: item.date, XAU: null, XAG: null }
    existing[item.metal_type] = item.price_try ?? item.price_usd
    accumulator.set(item.date, existing)
    return accumulator
  }, new Map())

  return [...rows.values()].sort((left, right) => new Date(left.date) - new Date(right.date))
}
