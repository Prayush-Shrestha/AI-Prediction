import { HistoryTable } from "../../components/HistoryTable";
import { SectionHead } from "../../components/ui";
import { Card } from "../../components/ui";

export default function HistoryPage() {
  return (
    <div className="space-y-3">
      <SectionHead
        title="Prediction History"
        sub="a prediction is scored only once its outcome is observable in the dataset"
      />
      <Card>
        <p className="text-[13px] text-muted">
          Rows with <i>pending</i> actual results refer to the latest session — the market has not
          moved yet. Use “Score pending predictions” after new data arrives.
        </p>
      </Card>
      <HistoryTable />
    </div>
  );
}
