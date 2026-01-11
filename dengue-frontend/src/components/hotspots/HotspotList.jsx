import { AlertTriangle, TrendingUp } from 'lucide-react';

const HotspotList = ({ hotspots, selectedDistrict, onSelect }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          Hotspot Districts
        </h3>
      </div>
      <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
        {hotspots.map((district) => (
          <button
            key={district.District}
            onClick={() => onSelect(district)}
            className={`w-full px-4 py-4 text-left hover:bg-gray-50 transition-colors ${
              selectedDistrict?.District === district.District ? 'bg-blue-50' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-medium text-gray-900">{district.District}</h4>
              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                {district.Risk_Level}
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <AlertTriangle className="w-4 h-4" />
                <span>{((district.High_Probability || 0) * 100).toFixed(1)}% prob</span>
              </div>
              <div className="flex items-center gap-1">
                <TrendingUp className="w-4 h-4" />
                <span>Priority: {(district.Hotspot_Priority || 0).toFixed(3)}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default HotspotList;