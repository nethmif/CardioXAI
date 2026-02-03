import React from 'react';
import { CLINICAL_MAPPING } from './constants';

const VerticalDiceTable = ({ diceData }) => {
  if (!diceData || diceData === "EMPTY") return null;

  try {
    const data = typeof diceData === 'string' ? JSON.parse(diceData) : diceData;
    const keys = Object.keys(data[0]);

    return (
      <div className="vertical-print-container border rounded shadow-sm">
        {/* Table Header Row for Scenarios */}
        <div className="d-flex bg-light border-bottom fw-bold py-2 text-center" style={{ fontSize: '12px' }}>
          <div style={{ width: '30%' }} className="text-start ps-2">Clinical Metric</div>
          {data.map((_, idx) => (
            <div key={idx} style={{ width: `${70 / data.length}%` }}>
              Scenario {idx + 1}
            </div>
          ))}
        </div>

        {/* Metric Rows */}
        {keys.map((key) => {
          const mapping = CLINICAL_MAPPING[key];
          
          return (
            <div key={key} className="d-flex border-bottom py-2 align-items-center" style={{ fontSize: '11px' }}>
              {/* Row Label */}
              <div className="fw-bold text-muted ps-2" style={{ width: '30%' }}>
                {mapping?.label || key.replace(/_/g, ' ')}
              </div>

              {/* Data for each of the 3 counterfactuals */}
              {data.map((scenario, idx) => {
                const rawVal = scenario[key];
                let displayVal = rawVal;
                
                if (mapping?.map) {
                  displayVal = mapping.map[Math.round(rawVal)] || rawVal;
                } else if (typeof rawVal === 'number') {
                  displayVal = rawVal.toFixed(1);
                }

                return (
                  <div key={idx} className="text-center" style={{ width: `${70 / data.length}%` }}>
                    <span className={key === 'target' || key === 'prediction' ? 'fw-bold text-primary' : ''}>
                      {displayVal} 
                      {mapping?.unit && <div className="text-muted" style={{ fontSize: '9px' }}>{mapping.unit}</div>}
                    </span>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    );
  } catch (e) {
    console.error("Vertical Table Parsing Error:", e);
    return <div className="text-danger">Error loading comparison data.</div>;
  }
};

export default VerticalDiceTable;