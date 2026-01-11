export const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

export const formatPercentage = (num) => {
  return `${(num * 100).toFixed(1)}%`;
};

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const getRiskColor = (risk) => {
  const colors = {
    High: 'red',
    Medium: 'yellow',
    Low: 'green',
  };
  return colors[risk] || 'gray';
};