const PredictionOverviewCorrected = ({ districts, onSelect, selectedDistricts }) => {
  const getRiskBadgeColor = (risk) => {
    const colors = {
      High: 'bg-red-100 text-red-800 border-red-200',
      Medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      Low: 'bg-green-100 text-green-800 border-green-200',
    };
    return colors[risk] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const isSelected = (district) => {
    return selectedDistricts.some(d => d.District === district.District);
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          District Predictions
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Select up to 4 districts to compare
        </p>
      </div>
      
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {districts.map((district) => (
            <button
              key={district.District}
              onClick={() => onSelect(district)}
              className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
                isSelected(district)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-semibold text-gray-900">{district.District}</h4>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getRiskBadgeColor(district.Risk_Level)}`}>
                  {district.Risk_Level}
                </span>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Score:</span>
                  <span className="font-medium text-gray-900">
                    {district.Risk_Score}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">High Prob:</span>
                  <span className="font-medium text-gray-900">
                    {((district.High_Probability || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Priority:</span>
                  <span className="font-medium text-gray-900">
                    {(district.Hotspot_Priority || 0).toFixed(3)}
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PredictionOverviewCorrected;