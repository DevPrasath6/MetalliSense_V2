import { useState } from "react";
import Card from "./Card";
import Badge from "./Badge";
import Button from "./Button";
import { synthesizeSpeech } from "../../services/copilotService";
import toast from "react-hot-toast";

const ExplanationCard = ({ explanation }) => {
  const [isSpeaking, setIsSpeaking] = useState(false);

  if (!explanation) return null;

  const handleReadAloud = async () => {
    if (isSpeaking) return;

    try {
      setIsSpeaking(true);
      const fullText = `
        ${explanation.summary || ''}
        ${explanation.key_factors && explanation.key_factors.length > 0 ? `Key factors: ${explanation.key_factors.join(", ")}` : ''}
        ${explanation.recommendation || ''}
      `;

      const audioBlob = await synthesizeSpeech(fullText);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
        toast.error("Failed to play audio");
      };

      await audio.play();
    } catch (error) {
      console.error("Text-to-Speech error:", error);
      toast.error("Failed to synthesize speech");
      setIsSpeaking(false);
    }
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case "low":
        return "success";
      case "medium":
        return "warning";
      case "high":
        return "danger";
      default:
        return "default";
    }
  };

  return (
    <Card className="mt-3 sm:mt-4">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 sm:gap-0 mb-3 sm:mb-4">
        <div>
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-1 sm:mb-2">
            AI Explanation
          </h3>
          {explanation.risk_level && (
            <Badge variant={getRiskColor(explanation.risk_level)}>
              Risk: {explanation.risk_level}
            </Badge>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleReadAloud}
          disabled={isSpeaking}
          className="self-start sm:self-auto"
        >
          {isSpeaking ? (
            <>
              <span className="animate-pulse">🔊</span> Speaking...
            </>
          ) : (
            <>🔊 Read Aloud</>
          )}
        </Button>
      </div>

      <div className="space-y-3 sm:space-y-4">
        <div>
          <h4 className="font-medium text-gray-700 text-sm sm:text-base mb-1 sm:mb-2">Summary</h4>
          <p className="text-gray-600 text-xs sm:text-sm">{explanation.summary}</p>
        </div>

        {explanation.key_factors && explanation.key_factors.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-700 text-sm sm:text-base mb-1 sm:mb-2">Key Factors</h4>
            <ul className="list-disc list-inside space-y-1">
              {explanation.key_factors.map((factor, index) => (
                <li key={index} className="text-gray-600 text-xs sm:text-sm">
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}

        {explanation.confidence && (
          <div>
            <h4 className="font-medium text-gray-700 text-sm sm:text-base mb-1 sm:mb-2">Confidence</h4>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="flex-1 bg-gray-200 rounded-full h-1.5 sm:h-2">
                <div
                  className="bg-emerald-600 h-1.5 sm:h-2 rounded-full transition-all duration-300"
                  style={{ width: `${explanation.confidence * 100}%` }}
                />
              </div>
              <span className="text-xs sm:text-sm font-medium text-gray-700">
                {(explanation.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        )}

        {explanation.recommendation && (
          <div>
            <h4 className="font-medium text-gray-700 text-sm sm:text-base mb-1 sm:mb-2">Recommendation</h4>
            <p className="text-gray-600 text-xs sm:text-sm">{explanation.recommendation}</p>
          </div>
        )}

        {explanation.action_items && explanation.action_items.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-700 text-sm sm:text-base mb-1 sm:mb-2">Action Items</h4>
            <ul className="space-y-1 sm:space-y-2">
              {explanation.action_items.map((item, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-emerald-600 mt-0.5 text-xs sm:text-sm">✓</span>
                  <span className="text-gray-600 text-xs sm:text-sm">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ExplanationCard;
