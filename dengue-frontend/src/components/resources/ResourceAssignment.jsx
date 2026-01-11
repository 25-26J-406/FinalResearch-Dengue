import { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import { adminAPI } from '../../services/api';

const ResourceAssignment = ({ availableResources, onAssign }) => {
  const [districts, setDistricts] = useState([]);
  const [formData, setFormData] = useState({
    district: '',
    Fogging_Units: 0,
    Health_Inspectors: 0,
    Inspection_Teams: 0,
    Treatment_Units: 0,
  });

  useEffect(() => {
      const fetchDistricts = async () => {
    try {
      const response = await adminAPI.getOverview();
      const districtList = response.data.districts || [];
      setDistricts(districtList);
    } catch (error) {
      console.error('Failed to fetch districts:', error);
    }
  };
    fetchDistricts();
  }, []);



  const handleChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      [key]: key === 'district' ? value : parseInt(value) || 0
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.district) return;
    onAssign(formData);
    setFormData({
      district: '',
      Fogging_Units: 0,
      Health_Inspectors: 0,
      Inspection_Teams: 0,
      Treatment_Units: 0,
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Assign Resources
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Select District
          </label>
          <select
            value={formData.district}
            onChange={(e) => handleChange('district', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Choose a district...</option>
            {districts.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        {Object.keys(availableResources || {}).map((key) => (
          <div key={key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {key.replace(/_/g, ' ')}
              <span className="text-xs text-gray-500 ml-2">
                (Available: {availableResources[key]})
              </span>
            </label>
            <input
              type="number"
              value={formData[key]}
              onChange={(e) => handleChange(key, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              min="0"
              max={availableResources[key]}
            />
          </div>
        ))}

        <button
          type="submit"
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Send className="w-4 h-4" />
          Assign Resources
        </button>
      </form>
    </div>
  );
};

export default ResourceAssignment;