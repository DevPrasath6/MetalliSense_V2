import React, { useState, useEffect, useContext } from "react";
import { OPCContext } from "../context/OPCContext";
import Card from "../components/common/Card";
import Button from "../components/common/Button";
import Table from "../components/common/Table";
import {
  connectSpectrometerOPC,
  disconnectSpectrometerOPC,
  requestOPCReading,
  getAllReadings,
  deleteReading,
} from "../services/spectrometerService";
import toast from "react-hot-toast";
import { formatDate, formatPercentage } from "../utils/formatters";
import { Trash2 } from "lucide-react";

const Spectrometer = () => {
  const { opcStatus } = useContext(OPCContext);
  const [readings, setReadings] = useState([]);
  const [latestReading, setLatestReading] = useState(null);
  const [loading, setLoading] = useState(false);
  const [requesting, setRequesting] = useState(false);

  useEffect(() => {
    fetchReadings();
  }, []);

  const fetchReadings = async () => {
    setLoading(true);
    try {
      const response = await getAllReadings();
      console.log("Spectrometer readings response:", response.data);
      const rawData =
        response.data.data?.data || response.data.data || response.data;
      const data = Array.isArray(rawData) ? rawData : [];
      console.log("Extracted readings:", data);
      setReadings(data);
      if (data.length > 0) {
        setLatestReading(data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch readings:", error);
      toast.error("Failed to load readings");
    } finally {
      setLoading(false);
    }
  };

  const handleRequestReading = async () => {
    setRequesting(true);
    try {
      const response = await requestOPCReading({ metalGrade: "SG-IRON" });
      const newReading = response.data.data?.reading || response.data.data;
      if (newReading) {
        setLatestReading(newReading);
      }
      toast.success("OPC reading received");
      await fetchReadings();
    } catch (error) {
      toast.error(
        error.response?.data?.message || "Failed to request OPC reading"
      );
    } finally {
      setRequesting(false);
    }
  };

  const handleDeleteReading = async (id) => {
    if (!window.confirm("Are you sure you want to delete this reading?"))
      return;

    try {
      await deleteReading(id);
      toast.success("Reading deleted successfully");
      fetchReadings();
    } catch (error) {
      toast.error("Failed to delete reading");
    }
  };

  const columns = [
    {
      header: "Timestamp",
      render: (row) => (
        <span className="font-mono text-sm">
          {formatDate(row.timestamp || row.createdAt)}
        </span>
      ),
    },
    {
      header: "Fe %",
      render: (row) => (
        <span className="font-mono">
          {formatPercentage(row.Fe || row.composition?.Fe || 0)}
        </span>
      ),
    },
    {
      header: "C %",
      render: (row) => (
        <span className="font-mono">
          {formatPercentage(row.C || row.composition?.C || 0)}
        </span>
      ),
    },
    {
      header: "Mn %",
      render: (row) => (
        <span className="font-mono">
          {formatPercentage(row.Mn || row.composition?.Mn || 0)}
        </span>
      ),
    },
    {
      header: "Si %",
      render: (row) => (
        <span className="font-mono">
          {formatPercentage(row.Si || row.composition?.Si || 0)}
        </span>
      ),
    },
    {
      header: "Actions",
      render: (row) => (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => handleDeleteReading(row._id)}
        >
          <Trash2 size={16} className="text-red-600" />
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Control Panel */}
      <Card title="OPC Control Panel">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div
              className={`h-3 w-3 rounded-full ${
                opcStatus.connected
                  ? "bg-green-500 animate-pulse"
                  : "bg-red-500"
              }`}
            />
            <span className="font-medium text-sm sm:text-base">
              Status: {opcStatus.connected ? "Connected" : "Disconnected"}
            </span>
          </div>
          <Button
            onClick={handleRequestReading}
            loading={requesting}
            disabled={!opcStatus.connected}
            className="self-start sm:self-auto"
          >
            Request Reading
          </Button>
        </div>
      </Card>

      {/* Latest Reading */}
      {latestReading && (
        <Card title="Latest Reading">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 sm:gap-4">
            {(latestReading.composition && typeof latestReading.composition === "object"
              ? (latestReading.composition instanceof Map
                  ? Array.from(latestReading.composition.entries())
                  : Object.entries(latestReading.composition))
              : Object.entries(latestReading)
            )
              .filter(
                ([key, val]) =>
                  !key.startsWith("_") &&
                  key !== "timestamp" &&
                  key !== "createdAt" &&
                  key !== "updatedAt" &&
                  key !== "notes" &&
                  key !== "is_synthetic" &&
                  key !== "deviation_applied" &&
                  key !== "deviation_elements" &&
                  typeof val === "number"
              )
              .map(([element, value]) => (
                <div key={element} className="p-3 sm:p-4 bg-dark-50 rounded-lg">
                  <span className="font-mono font-bold text-xs sm:text-sm text-dark-600">
                    {element}
                  </span>
                  <p className="text-lg sm:text-xl font-bold text-dark-900 mt-1">
                    {formatPercentage(value)}
                  </p>
                </div>
              ))}
          </div>
          <p className="text-xs text-dark-500 mt-3 sm:mt-4">
            Received:{" "}
            {formatDate(latestReading.timestamp || latestReading.createdAt)}
          </p>
        </Card>
      )}

      {/* Reading History */}
      <Card title="Reading History">
        <Table columns={columns} data={readings} loading={loading} />
      </Card>
    </div>
  );
};

export default Spectrometer;
