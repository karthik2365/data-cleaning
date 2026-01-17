import Hero from "@/src/components/Hero"
import Problem from "@/src/components/Problem"
import HowItWorks from "@/src/components/HowItWorks"
import WhyDifferent from "@/src/components/WhyDifferent"
import Features from "@/src/components/Features"
import TechStack from "@/src/components/TechStack"
import CTA from "@/src/components/CTA"
import Footer from "@/src/components/Footer"

export default function Page() {
  return (
    <div className="min-h-screen bg-white text-black font-mono">
      <Hero />
      <Problem />
      <HowItWorks />
      <WhyDifferent />
      <Features />
      <TechStack />
      <CTA />
      <Footer />
    </div>
  )
}
