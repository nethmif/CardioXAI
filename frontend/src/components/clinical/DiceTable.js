// import React from 'react';
// import { Alert } from 'react-bootstrap';
// import { CLINICAL_MAPPING } from './constants';

// const DiceTable = ({ diceData }) => {
//   if (!diceData || diceData === "EMPTY") {
//     return (
//       <div className="text-center py-3 text-muted">
//         <p className="small mb-0">No clinically achievable scenarios found for this patient's specific profile.</p>
//       </div>
//     );
//   }
//   try {
//     // const data = JSON.parse(diceData);
//     const data = diceData;
//     const headers = Object.keys(data[0]);

//     return (
//       <div className="table-responsive mt-3">
//         <table className="table table-bordered table-sm align-middle">
//           <thead className="table-light">
//             <tr>
//               {headers.map(key => (
//                 <th key={key} className="small text-nowrap">
//                   {CLINICAL_MAPPING[key]?.label || key}
//                 </th>
//               ))}
//             </tr>
//           </thead>
//           <tbody>
//             {data.map((row, index) => (
//               <tr key={index}>
//                 {headers.map((key, i) => {
//                   const rawVal = row[key];
//                   const mapping = CLINICAL_MAPPING[key];
                  
//                   let displayVal = rawVal;
//                   if (mapping?.map) {
//                     displayVal = mapping.map[Math.round(rawVal)] || rawVal;
//                   } else if (typeof rawVal === 'number') {
//                     displayVal = rawVal.toFixed(1);
//                   }

//                   return (
//                     <td key={i} className="small">
//                       <span className={key === 'target' ? 'fw-bold text-primary' : ''}>
//                         {displayVal} {mapping?.unit && <small className="text-muted">{mapping.unit}</small>}
//                       </span>
//                     </td>
//                   );
//                 })}
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//     );
//   } catch (e) { return <Alert variant="warning">Data Error</Alert>; }
// };

// export default DiceTable;

const DiceTable = ({ diceData }) => {
  // 1. Improved Guard Clause
  if (!diceData || diceData === "EMPTY" || (Array.isArray(diceData) && diceData.length === 0)) {
    return (
      <div className="text-center py-3 text-muted">
        <p className="small mb-0">No clinically achievable scenarios found.</p>
      </div>
    );
  }

  // 2. Hardened Parser to strip brackets if they still appear
  const parseVal = (val) => {
    if (val === null || val === undefined) return 0;
    if (typeof val === 'string') {
        // Removes brackets [ ] and quotes ' " then parses
        const clean = val.replace(/[\[\]'"]/g, '');
        return parseFloat(clean);
    }
    return val;
  };

  try {
    // 3. Ensure data is an array (handles if it arrives as string or object)
    const data = typeof diceData === 'string' ? JSON.parse(diceData) : diceData;
    const headers = Object.keys(data[0]);

    return (
      <div className="table-responsive mt-3">
        <table className="table table-bordered table-sm align-middle">
           <thead className="table-light">
             <tr>
               {headers.map(key => (
                <th key={key} className="small text-nowrap">
                  {CLINICAL_MAPPING[key]?.label || key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index}>
                {headers.map((key, i) => {
                  const rawVal = parseVal(row[key]); 
                  const mapping = CLINICAL_MAPPING[key];
                  
                  let displayVal = rawVal;
                  if (mapping?.map) {
                    displayVal = mapping.map[Math.round(rawVal)] || rawVal;
                  } else if (typeof rawVal === 'number') {
                    displayVal = isNaN(rawVal) ? "N/A" : rawVal.toFixed(1);
                  }

                  return (
                    <td key={i} className="small">
                      <span className={key === 'target' ? 'fw-bold text-primary' : ''}>
                        {displayVal} {mapping?.unit && <small className="text-muted">{mapping.unit}</small>}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  } catch (e) { return <Alert variant="warning">Format Error</Alert>; }
};
export default DiceTable;