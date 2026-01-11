import { useState, useEffect } from 'react';
import { TrendingUp, RefreshCw, Search } from 'lucide-react';
import { predictionsAPI, adminAPI } from '../services/api';
import PredictionOverview from '../components/predictions/PredictionOverview';
import DistrictComparison from '../components/predictions/DistrictComparison';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import SuccessAlert from '../components/common/SuccessAlert';

const Predictions = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [districts, setDistricts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDistricts, setSelectedDistricts] = useState([]);
  const [riskFilter, setRiskFilter] = useState('all');

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get overview data which contains all districts with predictions
      const response = await adminAPI.getOverview();
      const allDistricts = response.data.high_risk_districts || [];
      
      // Get hotspots data for additional info
      const hotspotsResponse = await predictionsAPI.getHotspots();
      const hotspots = hotspotsResponse.data.hotspots || [];
      
      // Combine data - use hotspots as primary source since they have full info
      setDistricts(hotspots);
    } catch (err) {
      setError(err.message || 'Failed to load predictions');
      console.error('Predictions error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePredictions = async () => {
    try {
      setGenerating(true);
      setError(null);
      
      await predictionsAPI.generatePredictions();
      setSuccess('Predictions generated successfully');
      setTimeout(() => setSuccess(null), 3000);
      
      await fetchPredictions();
    } catch (err) {
      setError(err.message || 'Failed to generate predictions');
    } finally {
      setGenerating(false);
    }
  };

  const handleDistrictSelect = (district) => {
    setSelectedDistricts(prev => {
      const exists = prev.find(d => d.District === district.District);
      if (exists) {
        return prev.filter(d => d.District !== district.District);
      }
      if (prev.length >= 4) {
        return prev;
      }
      return [...prev, district];
    });
  };

  const filteredDistricts = districts.filter(d => {
    const matchesSearch = d.District.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk = riskFilter === 'all' || d.Risk_Level === riskFilter;
    return matchesSearch && matchesRisk;
  });

  if (loading) {
    return <LoadingSpinner message="Loading predictions..." />;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Risk Predictions</h2>
          <p className="text-gray-600 mt-1">
            AI-powered dengue risk assessment for all districts
          </p>
        </div>
        <button
          onClick={handleGeneratePredictions}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          {generating ? 'Generating...' : 'Generate New'}
        </button>
      </div>

      {/* Alerts */}
      {error && <ErrorAlert message={error} onClose={() => setError(null)} />}
      {success && <SuccessAlert message={success} onClose={() => setSuccess(null)} />}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Total Districts</div>
          <div className="text-3xl font-bold text-gray-900">{districts.length}</div>
        </div>
        <div className="bg-red-50 rounded-lg shadow p-6">
          <div className="text-sm text-red-600 mb-1">High Risk</div>
          <div className="text-3xl font-bold text-red-900">
            {districts.filter(d => d.Risk_Level === 'High').length}
          </div>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow p-6">
          <div className="text-sm text-yellow-600 mb-1">Medium Risk</div>
          <div className="text-3xl font-bold text-yellow-900">
            {districts.filter(d => d.Risk_Level === 'Medium').length}
          </div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-6">
          <div className="text-sm text-green-600 mb-1">Low Risk</div>
          <div className="text-3xl font-bold text-green-900">
            {districts.filter(d => d.Risk_Level === 'Low').length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search districts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Risk Levels</option>
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>
        </div>
      </div>

      {/* District Comparison */}
      {selectedDistricts.length > 0 && (
        <DistrictComparison
          districts={selectedDistricts}
          onRemove={(district) => handleDistrictSelect(district)}
        />
      )}

      {/* Predictions Overview */}
      <PredictionOverview
        districts={filteredDistricts}
        onSelect={handleDistrictSelect}
        selectedDistricts={selectedDistricts}
      />
    </div>
  );
};

export default Predictions;
