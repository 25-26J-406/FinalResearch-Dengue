import { Package, Users, Activity } from 'lucide-react';

const HotspotDetails = ({ district, recommendations }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          {district.District}
        </h3>
        
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="p-4 bg-red-50 rounded-lg">
            <div className="text-sm text-red-600 mb-1">Risk Level</div>
            <div className="text-2xl font-bold text-red-900">{district.Risk_Level}</div>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-blue-600 mb-1">High Risk Probability</div>
            <div className="text-2xl font-bold text-blue-900">
              {((district.High_Probability || 0) * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b border-gray-200">
            <span className="text-gray-600">Risk Score</span>
            <span className="font-semibold text-gray-900">
              {district.Risk_Score}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-200">
            <span className="text-gray-600">Hotspot Priority</span>
            <span className="font-semibold text-gray-900">
              {(district.Hotspot_Priority || 0).toFixed(4)}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-200">
            <span className="text-gray-600">Low Risk Probability</span>
            <span className="font-semibold text-gray-900">
              {((district.Low_Probability || 0) * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-600">Medium Risk Probability</span>
            <span className="font-semibold text-gray-900">
              {((district.Medium_Probability || 0) * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {recommendations && (
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Recommended Resources
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <Package className="w-6 h-6 text-blue-600 mb-2" />
              <div className="text-sm text-blue-600 mb-1">Fogging Units</div>
              <div className="text-2xl font-bold text-blue-900">
                {recommendations.Fogging_Units}
              </div>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <Users className="w-6 h-6 text-green-600 mb-2" />
              <div className="text-sm text-green-600 mb-1">Inspectors</div>
              <div className="text-2xl font-bold text-green-900">
                {recommendations.Health_Inspectors}
              </div>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <Activity className="w-6 h-6 text-purple-600 mb-2" />
              <div className="text-sm text-purple-600 mb-1">Teams</div>
              <div className="text-2xl font-bold text-purple-900">
                {recommendations.Inspection_Teams}
              </div>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <Package className="w-6 h-6 text-orange-600 mb-2" />
              <div className="text-sm text-orange-600 mb-1">Treatment</div>
              <div className="text-2xl font-bold text-orange-900">
                {recommendations.Treatment_Units}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HotspotDetails;