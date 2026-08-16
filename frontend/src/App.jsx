import React, { useState } from 'react';
import { motion } from 'framer-motion';
import MolstarViewer from './components/MolstarViewer';

function App() {
  const [smiles, setSmiles] = useState('');
  const [moleculeData, setMoleculeData] = useState(null);

  const handleGenerate = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/physics/generate_3d', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ smiles })
      });
      const data = await res.json();
      setMoleculeData(data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen p-8 flex flex-col items-center">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel p-8 w-full max-w-4xl"
      >
        <h1 className="text-3xl font-bold mb-6 text-center text-blue-400">CoChem-SEED</h1>
        
        <div className="flex gap-4 mb-8">
          <input 
            type="text" 
            value={smiles}
            onChange={(e) => setSmiles(e.target.value)}
            placeholder="Enter SMILES string (e.g. CCO)"
            className="flex-1 bg-slate-800 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:border-blue-400"
          />
          <button 
            onClick={handleGenerate}
            className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded font-semibold transition-colors"
          >
            Generate 3D
          </button>
        </div>

        {moleculeData && (
          <div className="h-96 rounded-lg overflow-hidden bg-slate-900 border border-slate-700">
            <MolstarViewer xyzData={moleculeData.xyz} />
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default App;
