import { createContext, useContext } from "react";

export const HealthContext = createContext({
  health: null,
  refresh: async () => {},
});

export function useHealth() {
  return useContext(HealthContext);
}
