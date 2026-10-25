plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

// CI passes the Release tag vX.Y.Z as -PreleaseVersion=X.Y.Z; the Client only
// offers an update when versionCode grows, so it is derived from the tag.
val releaseVersion = providers.gradleProperty("releaseVersion").orNull
val releaseVersionCode = releaseVersion?.let {
    val parts = it.split(".").map(String::toInt)
    require(parts.size == 3 && parts[1] < 100 && parts[2] < 100) {
        "releaseVersion must be X.Y.Z with Y and Z below 100, got $it"
    }
    parts[0] * 10000 + parts[1] * 100 + parts[2]
}
val appKeystorePath = System.getenv("APP_KEYSTORE_PATH")

android {
    namespace = "{{APP_ID}}"
    compileSdk = 37

    defaultConfig {
        applicationId = "{{APP_ID}}"
        minSdk = 26
        targetSdk = 37
        versionCode = releaseVersionCode ?: 1
        versionName = releaseVersion ?: "0.0.0-dev"
    }

    signingConfigs {
        if (appKeystorePath != null) {
            create("release") {
                storeFile = file(appKeystorePath)
                storePassword = System.getenv("APP_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("APP_KEY_ALIAS")
                keyPassword = System.getenv("APP_KEY_PASSWORD")
                enableV2Signing = true
                enableV3Signing = true
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.findByName("release")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    debugImplementation(libs.androidx.ui.tooling)

    testImplementation(libs.junit)
}
