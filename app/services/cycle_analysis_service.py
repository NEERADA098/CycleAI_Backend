
class CycleAnalysisService:
    
    def analyze_irregularity(self, cycle_lengths: list[float]) -> dict:
        """
        Analyzes cycle patterns to detect irregularity and potential
        PCOS indicators. Does NOT diagnose — only flags patterns
        that warrant medical consultation.
        """
        if len(cycle_lengths) < 3:
            return {"status": "insufficient_data", "cycles_needed": 3}
        
        avg = sum(cycle_lengths) / len(cycle_lengths)
        variance = max(cycle_lengths) - min(cycle_lengths)
        long_cycles = [c for c in cycle_lengths if c > 35]
        
        flags = []
        
        # WHO definition: irregular if cycles vary by more than 7 days
        if variance > 7:
            flags.append("irregular_cycles")
        
        # Possible PCOS indicator: consistently long cycles
        if avg > 35:
            flags.append("consistently_long_cycles")
        
        # More than half the cycles are long
        if len(long_cycles) > len(cycle_lengths) / 2:
            flags.append("frequent_long_cycles")
        
        # Cycles getting progressively longer (oligomenorrhea pattern)
        if len(cycle_lengths) >= 4:
            recent = cycle_lengths[-3:]
            older = cycle_lengths[:-3]
            if sum(recent)/len(recent) > sum(older)/len(older) + 5:
                flags.append("worsening_irregularity")
        
        if not flags:
            return {
                "status": "regular",
                "average_cycle": round(avg, 1),
                "message": "Your cycles appear regular."
            }
        
        message = self._build_message(flags, avg)
        
        return {
            "status": "irregular",
            "flags": flags,
            "average_cycle": round(avg, 1),
            "cycle_variation": round(variance, 1),
            "message": message,
            "see_doctor": len(flags) >= 2
        }
    
    def _build_message(self, flags: list, avg: float) -> str:
        if "frequently_long_cycles" in flags or avg > 35:
            return (
                "Your cycles have been consistently longer than 35 days. "
                "This pattern, especially combined with symptoms like facial "
                "hair growth or acne, may be worth discussing with a doctor. "
                "Conditions like PCOS or thyroid issues can cause this pattern. "
                "Only a doctor can diagnose the cause."
            )
        if "irregular_cycles" in flags:
            return (
                "Your cycle lengths vary significantly. Some variation is normal, "
                "but consistent irregularity is worth mentioning to your doctor, "
                "especially if you have other symptoms."
            )
        return "Your cycles show some irregularity. Monitor for a few more months."


cycle_analysis_service = CycleAnalysisService()
