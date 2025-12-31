"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import AnimatedCounter from "../ui/AnimatedCounter";
import HeroDogPreviewCard from "./HeroDogPreviewCard";
import { getStatistics } from "../../services/animalsService";
import { reportError } from "../../utils/logger";

/**
 * Hero section for Dogs of Hope Canada
 * @param {Object} props
 * @param {Object} props.initialStatistics - Pre-fetched statistics
 * @param {Array} props.previewDogs - Dogs to show in hero preview cards
 */
export default function HeroSection({
  initialStatistics = null,
  previewDogs = [],
}) {
  const [statistics, setStatistics] = useState(initialStatistics);
  const [loading, setLoading] = useState(!initialStatistics);
  const [error, setError] = useState(null);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError(null);
      const stats = await getStatistics();
      setStatistics(stats);
    } catch (err) {
      reportError("Error fetching statistics", { error: err.message });
      setError("Unable to load statistics. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!initialStatistics) {
      fetchStatistics();
    }
  }, [initialStatistics]);

  return (
    <section className="hero-gradient relative overflow-hidden py-12 md:py-20 lg:py-24">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
          {/* Left Column - Hero Text and CTA */}
          <div className="flex-1 text-center lg:text-left">
            <h1 className="text-hero font-bold text-foreground mb-6 leading-tight">
              Hope for Every Paw 🐾
            </h1>
            <p className="text-body text-muted-foreground mb-8 max-w-2xl mx-auto lg:mx-0 leading-relaxed">
              Rescue, heal, and rehome dogs across Canada 🇨🇦. Join us at Dogs of
              Hope Canada and give a dog a forever home.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link href="/donate">
                <Button
                  size="lg"
                  className="w-full sm:w-auto bg-orange-600 hover:bg-orange-700 text-white px-8 py-3"
                >
                  Donate Now
                </Button>
              </Link>
              <Link href="/gallery">
                <Button
                  size="lg"
                  className="w-full sm:w-auto bg-white dark:bg-gray-800 text-orange-600 border-2 border-orange-600 hover:bg-orange-50 font-bold px-8 py-3"
                >
                  View Dogs
                </Button>
              </Link>
            </div>
          </div>

          {/* Right Column - Statistics & Preview Dogs */}
          <div className="flex-1 w-full max-w-lg">
            {loading && (
              <div className="space-y-6">
                <div className="bg-card/50 dark:bg-gray-800/70 backdrop-blur-sm rounded-lg p-6 animate-shimmer h-40"></div>
              </div>
            )}

            {error && (
              <div className="bg-card/80 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-6 text-center">
                <div className="text-muted-foreground mb-4">{error}</div>
                <Button onClick={fetchStatistics} variant="outline" size="sm">
                  Try again
                </Button>
              </div>
            )}

            {statistics && !loading && !error && (
              <div className="space-y-6">
                {/* Statistics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-card/80 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-6 text-center shadow-sm">
                    <div className="text-3xl md:text-4xl font-bold text-orange-600 mb-2">
                      <AnimatedCounter
                        value={statistics.total_dogs}
                        label="Dogs need homes"
                        className="block"
                      />
                    </div>
                    <div className="text-sm text-muted-foreground font-medium">
                      Dogs need homes
                    </div>
                  </div>

                  <div className="bg-card/80 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-6 text-center shadow-sm">
                    <div className="text-3xl md:text-4xl font-bold text-orange-600 mb-2">
                      <AnimatedCounter
                        value={statistics.total_organizations}
                        label="Rescue Organizations"
                        className="block"
                      />
                    </div>
                    <div className="text-sm text-muted-foreground font-medium">
                      Rescue Organizations
                    </div>
                  </div>

                  <div className="bg-card/80 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-6 text-center shadow-sm hover:bg-orange-50 transition-colors cursor-pointer">
                    <div className="text-3xl md:text-4xl font-bold text-orange-600 mb-2">
                      <AnimatedCounter
                        value={statistics.countries.length}
                        label="Countries"
                        className="block"
                      />
                    </div>
                    <div className="text-sm text-muted-foreground font-medium">
                      Countries
                    </div>
                  </div>
                </div>

                {/* Dog Preview Cards */}
                <div className="mt-4">
                  <div className="text-center mb-4">
                    <p className="text-sm text-muted-foreground font-medium">
                      Ready for their forever home
                    </p>
                  </div>

                  {previewDogs.length > 0 ? (
                    <div className="flex justify-center items-start gap-0 -space-x-3 py-4">
                      {previewDogs.slice(0, 3).map((dog, index) => (
                        <HeroDogPreviewCard
                          key={dog.id}
                          dog={dog}
                          index={index}
                          priority={index === 0}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground text-center py-4">
                      <Link
                        href="/gallery"
                        className="text-orange-600 hover:text-orange-700 hover:underline transition-colors"
                      >
                        Browse all dogs →
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
