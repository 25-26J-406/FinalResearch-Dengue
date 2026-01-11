import { CheckCircle, X } from 'lucide-react';

const SuccessAlert = ({ message, onClose }) => {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <div className="flex items-start">
        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 mr-3" />
        <div className="flex-1">
          <p className="text-sm text-green-700 font-medium">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-green-600 hover:text-green-800"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
};

export default SuccessAlert;