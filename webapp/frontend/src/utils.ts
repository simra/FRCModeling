/**
 * When modelEvent is 'all', the backend needs to know which year's match data
 * to use. Derive it from the predictionEvent key (format: <year><state><name>)
 * and return e.g. '2026all'. For a specific event key, return it unchanged.
 */
export function effectiveModelEvent(modelEvent: string, predictionEvent: string): string {
  if (modelEvent !== 'all') return modelEvent;
  const m = predictionEvent.match(/^(\d{4})/);
  return m ? `${m[1]}all` : modelEvent;
}
