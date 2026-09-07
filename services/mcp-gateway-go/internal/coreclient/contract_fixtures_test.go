package coreclient

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

// The Python side exports one pinned response per endpoint into
// packages/contracts/fixtures. Decoding each with DisallowUnknownFields proves
// the Go structs name every field the API emits; a field added on one side
// without the other fails here rather than at runtime.
func decodeStrict[T any](t *testing.T, name string) T {
	t.Helper()
	path := filepath.Join("..", "..", "..", "..", "packages", "contracts", "fixtures", name)
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read %s: %v (run `npm run eval` to regenerate fixtures)", path, err)
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	var value T
	if err := decoder.Decode(&value); err != nil {
		t.Fatalf("%s does not decode into %T: %v", name, value, err)
	}
	return value
}

func TestContractFixturesDecodeWithoutUnknownFields(t *testing.T) {
	health := decodeStrict[HealthEnvelope](t, "health.json")
	if health.Data.Service == "" || len(health.Data.Dependencies) == 0 {
		t.Fatalf("health fixture decoded empty: %+v", health.Data)
	}
	datasets := decodeStrict[ResponseEnvelope[DatasetStatusData]](t, "dataset_status.json")
	if datasets.Data.Count != len(datasets.Data.Datasets) {
		t.Fatalf("dataset count %d does not match %d entries", datasets.Data.Count, len(datasets.Data.Datasets))
	}
	snapshot := decodeStrict[ResponseEnvelope[MarketSnapshotData]](t, "market_snapshot.json")
	if snapshot.Data.Ticker == "" || snapshot.Data.Price <= 0 {
		t.Fatalf("snapshot fixture decoded empty: %+v", snapshot.Data)
	}
	history := decodeStrict[ResponseEnvelope[PriceHistoryData]](t, "price_history.json")
	if len(history.Data.Observations) == 0 {
		t.Fatalf("history fixture has no observations")
	}
	sentiment := decodeStrict[ResponseEnvelope[SentimentData]](t, "sentiment.json")
	if sentiment.Data.Label == "" || sentiment.Data.TextHash == "" {
		t.Fatalf("sentiment fixture decoded empty: %+v", sentiment.Data)
	}
	evidence := decodeStrict[ResponseEnvelope[EvidenceSearchData]](t, "evidence_search.json")
	if evidence.Data.Scorer == "" || evidence.Data.Count != len(evidence.Data.Results) {
		t.Fatalf("evidence fixture inconsistent: %+v", evidence.Data)
	}
	brief := decodeStrict[ResponseEnvelope[ResearchBriefData]](t, "research_brief.json")
	for _, section := range brief.Data.Sections {
		if len(section.References) != len(section.Bullets) {
			t.Fatalf("section %q: %d references for %d bullets", section.Title, len(section.References), len(section.Bullets))
		}
	}
	run := decodeStrict[ResponseEnvelope[SavedResearchRunData]](t, "saved_research_run.json")
	if run.Data.Output.Title != brief.Data.Title {
		t.Fatalf("saved run title %q differs from brief title %q", run.Data.Output.Title, brief.Data.Title)
	}
}
