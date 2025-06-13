export const formatCurrency = (amount: number, currency: string = 'EUR') => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatDate = (date: string | Date) => {
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
};

export const formatPercentage = (value: number) => {
  return `${(value * 100).toFixed(2)}%`;
};

export const formatNumber = (value: number) => {
  return new Intl.NumberFormat('fr-FR').format(value);
};

export const getRiskColor = (score: number) => {
  if (score >= 0.8) return 'text-red-600 bg-red-50';
  if (score >= 0.6) return 'text-orange-600 bg-orange-50';
  if (score >= 0.4) return 'text-yellow-600 bg-yellow-50';
  return 'text-green-600 bg-green-50';
};

export const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'text-green-600 bg-green-50';
    case 'pending':
      return 'text-yellow-600 bg-yellow-50';
    case 'flagged':
      return 'text-orange-600 bg-orange-50';
    case 'blocked':
      return 'text-red-600 bg-red-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
};