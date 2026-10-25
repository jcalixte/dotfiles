// AGP 9 bundles an older Kotlin; this classpath lifts it to the catalog's version,
// which the Compose compiler plugin must match exactly.
buildscript {
    dependencies {
        classpath(libs.kotlin.gradle.plugin)
    }
}

plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.compose) apply false
}
