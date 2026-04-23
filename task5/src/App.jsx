import { useEffect, useMemo, useRef, useState } from "react";
import Papa from "papaparse";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Scatter,
} from "recharts";

const CSV_URL =
  "https://docs.google.com/spreadsheets/d/e/2PACX-1vRY9gGqqZ8boFdk-bsVnD3k52kOpxb32zOfP1_8oKsRAuB8UrNA_MDQNX5s8WN_5U8mbrfk1GXKmCPK/pub?gid=1896498807&single=true&output=csv";

function mean(arr) {
  if (!arr.length) return 0;
  return arr.reduce((sum, val) => sum + val, 0) / arr.length;
}

function median(arr) {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[mid - 1] + sorted[mid]) / 2
    : sorted[mid];
}

function quartile(arr, q) {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  }
  return sorted[base];
}

function stdDev(arr) {
  if (arr.length < 2) return 0;
  const avg = mean(arr);
  const variance =
    arr.reduce((sum, val) => sum + (val - avg) ** 2, 0) / (arr.length - 1);
  return Math.sqrt(variance);
}

function iqr(arr) {
  return quartile(arr, 0.75) - quartile(arr, 0.25);
}

function iqrBounds(arr, multiplier = 1.5) {
  const q1 = quartile(arr, 0.25);
  const q3 = quartile(arr, 0.75);
  const iqrVal = q3 - q1;
  return {
    lower: q1 - multiplier * iqrVal,
    upper: q3 + multiplier * iqrVal,
  };
}

function zScore(value, avg, std) {
  if (std === 0) return 0;
  return (value - avg) / std;
}

function movingAverage(values, windowSize = 5) {
  return values.map((_, i) => {
    const start = Math.max(0, i - windowSize + 1);
    const slice = values.slice(start, i + 1);
    return mean(slice);
  });
}

function gaussianElimination(matrix, vector) {
  const n = matrix.length;
  const a = matrix.map((row) => [...row]);
  const b = [...vector];

  for (let i = 0; i < n; i++) {
    let maxRow = i;
    for (let k = i + 1; k < n; k++) {
      if (Math.abs(a[k][i]) > Math.abs(a[maxRow][i])) {
        maxRow = k;
      }
    }

    [a[i], a[maxRow]] = [a[maxRow], a[i]];
    [b[i], b[maxRow]] = [b[maxRow], b[i]];

    const pivot = a[i][i];
    if (Math.abs(pivot) < 1e-12) {
      return new Array(n).fill(0);
    }

    for (let j = i; j < n; j++) {
      a[i][j] /= pivot;
    }
    b[i] /= pivot;

    for (let k = 0; k < n; k++) {
      if (k === i) continue;
      const factor = a[k][i];
      for (let j = i; j < n; j++) {
        a[k][j] -= factor * a[i][j];
      }
      b[k] -= factor * b[i];
    }
  }

  return b;
}

function polynomialRegression(yValues, degree) {
  const n = yValues.length;
  const xValues = Array.from({ length: n }, (_, i) => i);

  const m = degree + 1;
  const ata = Array.from({ length: m }, () => Array(m).fill(0));
  const atb = Array(m).fill(0);

  for (let row = 0; row < n; row++) {
    const x = xValues[row];
    const y = yValues[row];
    const powers = Array.from({ length: m }, (_, p) => x ** p);

    for (let i = 0; i < m; i++) {
      atb[i] += powers[i] * y;
      for (let j = 0; j < m; j++) {
        ata[i][j] += powers[i] * powers[j];
      }
    }
  }

  const coeffs = gaussianElimination(ata, atb);

  return xValues.map((x) => {
    let y = 0;
    for (let i = 0; i < coeffs.length; i++) {
      y += coeffs[i] * x ** i;
    }
    return y;
  });
}

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(2) : "0.00";
}

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chartType, setChartType] = useState("line");
  const [selectedMine, setSelectedMine] = useState("Total");
  const [trendDegree, setTrendDegree] = useState(2);
  const [zThreshold, setZThreshold] = useState(2.5);
  const [iqrMultiplier, setIqrMultiplier] = useState(1.5);
  const [movingAvgWindow, setMovingAvgWindow] = useState(5);
  const [movingAvgPercent, setMovingAvgPercent] = useState(30);

  const reportRef = useRef(null);

  useEffect(() => {
    Papa.parse(CSV_URL, {
      download: true,
      header: true,
      dynamicTyping: true,
      complete: (result) => {
        const cleaned = result.data
          .filter((row) => row.Date && row.Mine && row.Output !== undefined)
          .map((row) => ({
            Date: String(row.Date).trim(),
            Mine: String(row.Mine).trim(),
            Output: Number(row.Output),
          }))
          .filter((row) => !Number.isNaN(row.Output));

        setData(cleaned);
        setLoading(false);
      },
      error: (err) => {
        console.error("CSV load error:", err);
        setLoading(false);
      },
    });
  }, []);

  const mines = useMemo(() => {
    const unique = [...new Set(data.map((row) => row.Mine))];
    return unique;
  }, [data]);

  const statsByMine = useMemo(() => {
    const grouped = {};

    data.forEach((row) => {
      if (!grouped[row.Mine]) grouped[row.Mine] = [];
      grouped[row.Mine].push(row.Output);
    });

    return Object.entries(grouped).map(([mine, values]) => ({
      mine,
      count: values.length,
      mean: mean(values),
      stdDev: stdDev(values),
      median: median(values),
      iqr: iqr(values),
      q1: quartile(values, 0.25),
      q3: quartile(values, 0.75),
      min: Math.min(...values),
      max: Math.max(...values),
      values,
    }));
  }, [data]);

  const statsMap = useMemo(() => {
    const map = {};
    statsByMine.forEach((item) => {
      map[item.mine] = item;
    });
    return map;
  }, [statsByMine]);

  const chartData = useMemo(() => {
    const groupedByDate = {};

    data.forEach(({ Date, Mine, Output }) => {
      if (!groupedByDate[Date]) groupedByDate[Date] = { Date };
      groupedByDate[Date][Mine] = Output;
    });

    return Object.values(groupedByDate);
  }, [data]);

  const seriesData = useMemo(() => {
    if (!selectedMine || !statsMap[selectedMine]) return [];

    const mineRows = data.filter((row) => row.Mine === selectedMine);
    const values = mineRows.map((row) => row.Output);

    const mineStats = statsMap[selectedMine];
    const bounds = iqrBounds(values, iqrMultiplier);
    const ma = movingAverage(values, movingAvgWindow);
    const trend = polynomialRegression(values, trendDegree);

    return mineRows.map((row, index) => {
      const z = zScore(row.Output, mineStats.mean, mineStats.stdDev);
      const maDeviation =
        ma[index] === 0 ? 0 : Math.abs(row.Output - ma[index]) / ma[index];

      return {
        index,
        Date: row.Date,
        Output: row.Output,
        Trend: trend[index],
        MovingAverage: ma[index],
        zScore: z,
        zAnomaly: Math.abs(z) > zThreshold,
        iqrAnomaly: row.Output < bounds.lower || row.Output > bounds.upper,
        maAnomaly: maDeviation > movingAvgPercent / 100,
        maDeviation,
      };
    });
  }, [
    data,
    selectedMine,
    statsMap,
    zThreshold,
    iqrMultiplier,
    movingAvgWindow,
    movingAvgPercent,
    trendDegree,
  ]);

  const zAnomalies = useMemo(() => {
    return seriesData.filter((row) => row.zAnomaly);
  }, [seriesData]);

  const iqrAnomalies = useMemo(() => {
    return seriesData.filter((row) => row.iqrAnomaly);
  }, [seriesData]);

  const maAnomalies = useMemo(() => {
    return seriesData.filter((row) => row.maAnomaly);
  }, [seriesData]);

  const combinedAnomalies = useMemo(() => {
    return seriesData.filter(
      (row) => row.zAnomaly || row.iqrAnomaly || row.maAnomaly
    );
  }, [seriesData]);

  async function exportPdf() {
    const element = reportRef.current;
    if (!element) return;

    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: "#0f1220",
      useCORS: true,
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");

    const pdfWidth = 210;
    const pdfHeight = 297;
    const margin = 10;
    const imgWidth = pdfWidth - margin * 2;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = margin;

    pdf.addImage(imgData, "PNG", margin, position, imgWidth, imgHeight);
    heightLeft -= pdfHeight - margin * 2;

    while (heightLeft > 0) {
      pdf.addPage();
      position = margin - (imgHeight - heightLeft);
      pdf.addImage(imgData, "PNG", margin, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight - margin * 2;
    }

    pdf.save(`mining-report-${selectedMine}.pdf`);
  }

  const selectedStats = statsMap[selectedMine];

  if (loading) {
    return (
      <div style={styles.page}>
        <h1 style={styles.title}>Mining Dashboard</h1>
        <p>Loading data...</p>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <div style={styles.topBar}>
        <h1 style={styles.title}>Mining Dashboard</h1>
        <button style={styles.button} onClick={exportPdf}>
          Export PDF Report
        </button>
      </div>

      <div ref={reportRef}>
        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>Controls</h2>

          <div style={styles.controlsGrid}>
            <label style={styles.label}>
              Mine / Total
              <select
                style={styles.select}
                value={selectedMine}
                onChange={(e) => setSelectedMine(e.target.value)}
              >
                {mines.map((mine) => (
                  <option key={mine} value={mine}>
                    {mine}
                  </option>
                ))}
              </select>
            </label>

            <label style={styles.label}>
              Chart Type
              <select
                style={styles.select}
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
              >
                <option value="line">Line</option>
                <option value="bar">Bar</option>
                <option value="stacked">Stacked</option>
              </select>
            </label>

            <label style={styles.label}>
              Trendline Degree
              <select
                style={styles.select}
                value={trendDegree}
                onChange={(e) => setTrendDegree(Number(e.target.value))}
              >
                <option value={1}>1</option>
                <option value={2}>2</option>
                <option value={3}>3</option>
                <option value={4}>4</option>
              </select>
            </label>

            <label style={styles.label}>
              Z-score Threshold
              <input
                style={styles.input}
                type="number"
                step="0.1"
                value={zThreshold}
                onChange={(e) => setZThreshold(Number(e.target.value))}
              />
            </label>

            <label style={styles.label}>
              IQR Multiplier
              <input
                style={styles.input}
                type="number"
                step="0.1"
                value={iqrMultiplier}
                onChange={(e) => setIqrMultiplier(Number(e.target.value))}
              />
            </label>

            <label style={styles.label}>
              Moving Avg Window
              <input
                style={styles.input}
                type="number"
                min="2"
                value={movingAvgWindow}
                onChange={(e) => setMovingAvgWindow(Number(e.target.value))}
              />
            </label>

            <label style={styles.label}>
              Moving Avg Distance %
              <input
                style={styles.input}
                type="number"
                min="1"
                value={movingAvgPercent}
                onChange={(e) => setMovingAvgPercent(Number(e.target.value))}
              />
            </label>
          </div>
        </div>

        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Mean</div>
            <div style={styles.statValue}>
              {selectedStats ? formatNumber(selectedStats.mean) : "0.00"}
            </div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Std Dev</div>
            <div style={styles.statValue}>
              {selectedStats ? formatNumber(selectedStats.stdDev) : "0.00"}
            </div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Median</div>
            <div style={styles.statValue}>
              {selectedStats ? formatNumber(selectedStats.median) : "0.00"}
            </div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>IQR</div>
            <div style={styles.statValue}>
              {selectedStats ? formatNumber(selectedStats.iqr) : "0.00"}
            </div>
          </div>
        </div>

        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>
            {selectedMine} — Output Analysis
          </h2>

          <div style={{ width: "100%", height: 430 }}>
            <ResponsiveContainer>
              {chartType === "line" ? (
                <LineChart data={seriesData}>
                  <CartesianGrid stroke="#3a415e" />
                  <XAxis dataKey="Date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="Output"
                    name="Output"
                    strokeWidth={2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="Trend"
                    name={`Trend (deg ${trendDegree})`}
                    strokeDasharray="6 4"
                    dot={false}
                  />
                  <Scatter
                    name="Anomalies"
                    data={combinedAnomalies}
                    fill="red"
                  />
                </LineChart>
              ) : chartType === "bar" ? (
                <BarChart data={seriesData}>
                  <CartesianGrid stroke="#3a415e" />
                  <XAxis dataKey="Date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Output" name="Output" />
                  <Line
                    type="monotone"
                    dataKey="Trend"
                    name={`Trend (deg ${trendDegree})`}
                    strokeDasharray="6 4"
                    dot={false}
                  />
                  <Scatter
                    name="Anomalies"
                    data={combinedAnomalies}
                    fill="red"
                  />
                </BarChart>
              ) : (
                <AreaChart data={seriesData}>
                  <CartesianGrid stroke="#3a415e" />
                  <XAxis dataKey="Date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="Output"
                    name="Output"
                    stackId="1"
                  />
                  <Line
                    type="monotone"
                    dataKey="Trend"
                    name={`Trend (deg ${trendDegree})`}
                    strokeDasharray="6 4"
                    dot={false}
                  />
                  <Scatter
                    name="Anomalies"
                    data={combinedAnomalies}
                    fill="red"
                  />
                </AreaChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>

        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>Statistics by Mine</h2>
          <div style={{ overflowX: "auto" }}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th>Mine</th>
                  <th>Count</th>
                  <th>Mean</th>
                  <th>Std Dev</th>
                  <th>Median</th>
                  <th>IQR</th>
                  <th>Min</th>
                  <th>Max</th>
                </tr>
              </thead>
              <tbody>
                {statsByMine.map((row) => (
                  <tr key={row.mine}>
                    <td>{row.mine}</td>
                    <td>{row.count}</td>
                    <td>{formatNumber(row.mean)}</td>
                    <td>{formatNumber(row.stdDev)}</td>
                    <td>{formatNumber(row.median)}</td>
                    <td>{formatNumber(row.iqr)}</td>
                    <td>{formatNumber(row.min)}</td>
                    <td>{formatNumber(row.max)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={styles.anomalyGrid}>
          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>Z-score Anomalies</h2>
            {zAnomalies.length === 0 ? (
              <p>No z-score anomalies.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Output</th>
                    <th>Z-score</th>
                  </tr>
                </thead>
                <tbody>
                  {zAnomalies.map((row, index) => (
                    <tr key={`z-${index}`}>
                      <td>{row.Date}</td>
                      <td>{formatNumber(row.Output)}</td>
                      <td>{formatNumber(row.zScore)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div style={styles.card}>
            <h2 style={styles.sectionTitle}>IQR Anomalies</h2>
            {iqrAnomalies.length === 0 ? (
              <p>No IQR anomalies.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Output</th>
                  </tr>
                </thead>
                <tbody>
                  {iqrAnomalies.map((row, index) => (
                    <tr key={`iqr-${index}`}>
                      <td>{row.Date}</td>
                      <td>{formatNumber(row.Output)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>Moving Average Distance Anomalies</h2>
          {maAnomalies.length === 0 ? (
            <p>No moving average anomalies.</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Output</th>
                  <th>Distance %</th>
                </tr>
              </thead>
              <tbody>
                {maAnomalies.map((row, index) => (
                  <tr key={`ma-${index}`}>
                    <td>{row.Date}</td>
                    <td>{formatNumber(row.Output)}</td>
                    <td>{formatNumber(row.maDeviation * 100)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>Detailed Summary</h2>
          <p>
            This report analyzes <strong>{selectedMine}</strong> using three
            anomaly methods: z-score, IQR rule, and percent distance from moving
            average. The trendline is a polynomial of degree{" "}
            <strong>{trendDegree}</strong>.
          </p>
          <p>
            Total detected anomalies for the current selection:{" "}
            <strong>{combinedAnomalies.length}</strong>.
          </p>
          <p>
            Thresholds currently used: z-score {zThreshold}, IQR multiplier{" "}
            {iqrMultiplier}, moving average window {movingAvgWindow}, moving
            average distance {movingAvgPercent}%.
          </p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#0f1220",
    color: "#f2f2f2",
    padding: "24px",
    fontFamily: "Arial, sans-serif",
  },
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "16px",
    flexWrap: "wrap",
    marginBottom: "20px",
  },
  title: {
    margin: 0,
    fontSize: "52px",
    lineHeight: 1.1,
  },
  button: {
    background: "#2f80ed",
    color: "white",
    border: "none",
    borderRadius: "10px",
    padding: "12px 18px",
    cursor: "pointer",
    fontSize: "15px",
    fontWeight: "bold",
  },
  card: {
    background: "#171b2e",
    borderRadius: "14px",
    padding: "20px",
    marginBottom: "24px",
    boxShadow: "0 6px 18px rgba(0,0,0,0.25)",
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: "16px",
    fontSize: "24px",
  },
  controlsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "14px",
  },
  label: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    fontSize: "14px",
    color: "#d7dcf0",
  },
  select: {
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #444b68",
    background: "#111526",
    color: "#fff",
  },
  input: {
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #444b68",
    background: "#111526",
    color: "#fff",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
    marginBottom: "24px",
  },
  statCard: {
    background: "#171b2e",
    borderRadius: "14px",
    padding: "18px",
    boxShadow: "0 6px 18px rgba(0,0,0,0.25)",
  },
  statLabel: {
    color: "#aeb7d8",
    fontSize: "14px",
    marginBottom: "8px",
  },
  statValue: {
    fontSize: "28px",
    fontWeight: "bold",
  },
  anomalyGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "24px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    background: "#111526",
    color: "#f2f2f2",
  },
};