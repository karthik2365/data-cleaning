import { useState } from "react";
import Features from "./components/features"
import Footer from "./components/Footer"
import Hero from "./components/hero"
import HowItWorks from "./components/Howitworks"
import Problem from "./components/Problem"
import TechStack from "./components/Techstack"
import WhyDifferent from "./components/Whydifferent"
import DataCleaner from "./components/DataCleaner"
import CTA from "./components/CTA.JSX";

function App() {
  const [showCleaner, setShowCleaner] = useState(false);

  if (showCleaner) {
    return <DataCleaner onBack={() => setShowCleaner(false)} />;
  }

  return (
    <div className="min-h-screen bg-white text-black font-mono">
      <Hero />
      <Problem />
      <HowItWorks />
      <WhyDifferent />
      <Features />
      <TechStack />
      <CTA onNavigate={() => setShowCleaner(true)} />
      <Footer />
    </div>
  )
}

export default App
