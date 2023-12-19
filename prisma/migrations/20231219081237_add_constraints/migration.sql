-- CreateTable
CREATE TABLE "spins_hourly" (
    "date" TIMESTAMP(6) NOT NULL,
    "user_id" VARCHAR(7) NOT NULL,
    "country" VARCHAR(2) NOT NULL,
    "total_spins" INTEGER NOT NULL,

    CONSTRAINT "spins_hourly_pkey" PRIMARY KEY ("date","user_id","country")
);
ALTER TABLE "spins_hourly" ADD CONSTRAINT "total_spins" CHECK ("total_spins" >= 0);

-- CreateTable
CREATE TABLE "purchases" (
    "transaction_id" UUID NOT NULL,
    "date" TIMESTAMP(6) NOT NULL,
    "user_id" VARCHAR(7) NOT NULL,
    "currency" VARCHAR(3) NOT NULL DEFAULT 'USD',
    "revenue" DOUBLE PRECISION NOT NULL,

    CONSTRAINT "purchases_pkey" PRIMARY KEY ("transaction_id")
);
ALTER TABLE "purchases" ADD CONSTRAINT "revenue" CHECK ("revenue" >= 0);

-- CreateTable
CREATE TABLE "aggregated" (
    "date" TIMESTAMP(6) NOT NULL,
    "user_id" VARCHAR(7) NOT NULL,
    "country" VARCHAR(2),
    "total_spins" INTEGER,
    "total_revenue" DOUBLE PRECISION,
    "total_purchases" INTEGER,
    "avg_revenue_per_purchase" DOUBLE PRECISION,
    "total_daily_revenue" DOUBLE PRECISION,

    CONSTRAINT "aggregated_pkey" PRIMARY KEY ("date","user_id")
);
