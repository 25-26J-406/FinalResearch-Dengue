import { useState, useEffect } from 'react';
import { AlertTriangle, MapPin, TrendingUp } from 'lucide-react';
import { predictionsAPI } from '../services/api';
import HotspotList from '../components/hotspots/HotspotList';
import HotspotDetails from '../components/hotspots/HotspotDetails';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';

const Hotspots = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hotspots, setHotspots] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [recommendations, setRecommendations] = useState({});

  useEffect(() => {
    fetchHotspotData();
  }, []);

  const fetchHotspotData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [hotspotsRes, recommendationsRes] = await Promise.all([
        predictionsAPI.getHotspots(),
        predictionsAPI.getRecommendations(),
      ]);
      
      const hotspotsData = hotspotsRes.data.hotspots || [];
      const recommendationsData = recommendationsRes.data.recommendations || [];
      
      setHotspots(hotspotsData);
      
      // Convert recommendations array to object keyed by district
      const recsObject = {};
      recommendationsData.forEach(rec => {
        recsObject[rec.District] = rec;
      });
      setRecommendations(recsObject);
    } catch (err) {
      setError(err.message || 'Failed to load hotspot data');
      console.error('Hotspots error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading hotspots..." />;
  }

  if (error) {
    return <ErrorAlert message={error} onRetry={fetchHotspotData} />;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Hotspot Detection</h2>
        <p className="text-gray-600 mt-1">
          High-risk districts requiring immediate intervention
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="w-8 h-8 text-red-600" />
            <span className="text-3xl font-bold text-red-900">
              {hotspots.length}
            </span>
          </div>
          <h3 className="text-sm font-medium text-red-800">Active Hotspots</h3>
          <p className="text-xs text-red-600 mt-1">
            Districts with high dengue risk
          </p>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <MapPin className="w-8 h-8 text-orange-600" />
            <span className="text-3xl font-bold text-orange-900">
              {hotspots.filter(h => (h.High_Probability || 0) > 0.95).length}
            </span>
          </div>
          <h3 className="text-sm font-medium text-orange-800">
            Critical Areas
          </h3>
          <p className="text-xs text-orange-600 mt-1">
            High confidence hotspots
          </p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8 text-yellow-600" />
            <span className="text-3xl font-bold text-yellow-900">
              {Object.keys(recommendations).length}
            </span>
          </div>
          <h3 className="text-sm font-medium text-yellow-800">
            Resource Plans
          </h3>
          <p className="text-xs text-yellow-600 mt-1">
            Districts with recommendations
          </p>
        </div>
      </div>

      {/* Main Content */}
      {hotspots.length === 0 ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-12 text-center">
          <AlertTriangle className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-green-900 mb-2">
            No Active Hotspots
          </h3>
          <p className="text-green-700">
            All districts are currently at low or medium risk levels.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <HotspotList
              hotspots={hotspots}
              selectedDistrict={selectedDistrict}
              onSelect={setSelectedDistrict}
            />
          </div>
          <div className="lg:col-span-2">
            {selectedDistrict ? (
              <HotspotDetails
                district={selectedDistrict}
                recommendations={recommendations[selectedDistrict.District]}
              />
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a District
                </h3>
                <p className="text-gray-600">
                  Choose a hotspot from the list to view detailed information
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Hotspots;